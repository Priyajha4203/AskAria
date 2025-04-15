import os 

files = os.listdir("data")

output_path = "data/main.txt"
for item in files:
    with open(output_path , "a+", encoding = 'utf-8') as f:
        print(item)
        with open(f"data/{item}" , "r",encoding='utf-8') as g:
            data = g.read()
            f.write(data)