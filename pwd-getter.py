with open("foo.txt", "a") as f:

    for i in range(65, 91):
        for j in range(65, 91):
            for k in range(65, 91):
                for m in range(65, 91):
                    if(i!=j!=k):
                        f.write(f"{chr(i)}{chr(j)}{chr(k)}{chr(m)}\n")
                # print(f"{chr(i)}{chr(j)}{chr(k)}")

