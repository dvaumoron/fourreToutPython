
def printContentType():
    print("Content-Type: text/html")
    print()

def readTemplate(path):
    buffer = []
    with open(path) as f:
        needPrint = True
        for line in f:
            line = line.rstrip("\n")
            line = line.replace("'", "\\'")
            line = line.replace("<%=", "',")
            start = line.count("<%")
            line = line.replace("<%", "', sep='')\n")
            line = line.replace("=%>", ",'")
            end = line.count("%>")
            line = line.replace("%>", "\nprint('")

            diff = start - end
            if diff == 0:
                if needPrint:
                    buffer.append("print('")
                    buffer.append(line)
                    buffer.append("\\n', sep='')\n")
                else:
                    buffer.append(line)
                    buffer.append("\n")
            elif diff > 0:
                needPrint = False 
                buffer.append("print('")
                buffer.append(line)
                buffer.append("\n")
            else:
                needPrint = True
                buffer.append(line)
                buffer.append("\\n', sep='')\n")
    return "".join(buffer)
