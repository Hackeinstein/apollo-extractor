with open("link.txt","r") as file:
    link=file.read()
    link=link.replace("?page=1","?page=2")
    print(link)