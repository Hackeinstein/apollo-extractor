package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strconv"
	"sync"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/widget"
	"github.com/go-rod/rod"
	"github.com/go-rod/rod/lib/input"
)

// ApolloHunterApp holds the application state
type ApolloHunterApp struct {
	Driver         *rod.Browser
	RecoveredCount int
	Data           []string
	Running        bool
	Mutex          sync.Mutex
	Delay          int
}

// NewApolloHunterApp initializes a new ApolloHunterApp
func NewApolloHunterApp() *ApolloHunterApp {
	return &ApolloHunterApp{
		Driver:         rod.New().MustConnect(),
		RecoveredCount: 0,
		Data:           []string{},
		Running:        false,
		Delay:          0,
	}
}

// SaveCookies saves the browser cookies to a file
func (app *ApolloHunterApp) SaveCookies() {
	cookies, err := app.Driver.MustPage("").Cookies()
	if err != nil {
		log.Println("Failed to get cookies:", err)
		return
	}
	data, err := json.Marshal(cookies)
	if err != nil {
		log.Println("Failed to serialize cookies:", err)
		return
	}
	err = ioutil.WriteFile("apollo_cookies.json", data, 0644)
	if err != nil {
		log.Println("Failed to save cookies:", err)
	}
	log.Println("Cookies saved successfully.")
}

// LoadCookies loads the cookies from a file
func (app *ApolloHunterApp) LoadCookies() {
	data, err := ioutil.ReadFile("apollo_cookies.json")
	if err != nil {
		log.Println("Failed to load cookies:", err)
		return
	}
	var cookies []*rod.Cookie
	err = json.Unmarshal(data, &cookies)
	if err != nil {
		log.Println("Failed to parse cookies:", err)
		return
	}
	page := app.Driver.MustPage("")
	for _, cookie := range cookies {
		page.MustSetCookies(cookie)
	}
	log.Println("Cookies loaded successfully.")
}

// StartScraping starts the scraping process
func (app *ApolloHunterApp) StartScraping(link string) {
	app.Running = true
	go func() {
		defer func() {
			app.Running = false
			log.Println("Scraping stopped.")
		}()
		page := app.Driver.MustPage(link)

		rowCounter := 1
		for app.Running {
			// Example row scraping logic
			rows := page.MustElements("div[role='row']")
			if len(rows) > 0 {
				row := rows[rowCounter%len(rows)]
				name := row.MustElement("a[class*='zp_p2Xqs']").MustText()
				email := "N/A"
				log.Printf("Scraped Row %d: %s - %s\n", rowCounter, name, email)
				app.Mutex.Lock()
				app.Data = append(app.Data, fmt.Sprintf("Name: %s, Email: %s", name, email))
				app.RecoveredCount++
				app.Mutex.Unlock()
				rowCounter++
			}

			time.Sleep(time.Duration(app.Delay) * time.Second)
		}
	}()
}

// SaveData saves the scraped data to a file
func (app *ApolloHunterApp) SaveData() {
	file, err := os.Create("leads.txt")
	if err != nil {
		log.Println("Failed to save data:", err)
		return
	}
	defer file.Close()
	for _, lead := range app.Data {
		file.WriteString(lead + "\n")
	}
	log.Println("Data saved successfully to leads.txt.")
}

// BuildUI builds the Fyne application interface
func (app *ApolloHunterApp) BuildUI(a fyne.App) fyne.Window {
	w := a.NewWindow("Apollo Hunter")
	w.Resize(fyne.NewSize(500, 400))

	// Input fields and buttons
	delayInput := widget.NewEntry()
	delayInput.SetPlaceHolder("Delay (seconds)")

	statusLabel := widget.NewLabel("Status: Ready")
	recoveredLabel := widget.NewLabel("Recovered Leads: 0")

	startButton := widget.NewButton("Start", func() {
		delay, err := strconv.Atoi(delayInput.Text)
		if err != nil {
			statusLabel.SetText("Invalid delay value")
			return
		}
		app.Delay = delay
		statusLabel.SetText("Scraping started...")
		app.StartScraping("https://app.apollo.io")
	})

	stopButton := widget.NewButton("Stop", func() {
		app.Running = false
		statusLabel.SetText("Scraping stopped.")
	})

	saveButton := widget.NewButton("Save Data", func() {
		app.SaveData()
	})

	// Layout
	content := container.NewVBox(
		widget.NewLabel("Apollo Hunter"),
		widget.NewLabel("Delay time (seconds):"),
		delayInput,
		startButton,
		stopButton,
		saveButton,
		recoveredLabel,
		statusLabel,
	)

	w.SetContent(content)
	return w
}

func main() {
	a := app.New()
	appInstance := NewApolloHunterApp()
	defer appInstance.Driver.Close()
	w := appInstance.BuildUI(a)
	w.ShowAndRun()
}
