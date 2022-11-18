
import datetime
import subprocess

now = datetime.datetime.now

run = subprocess.run

start = now()

res = run(["java", "-cp", "..\\javaWorkspace\\chiffre\\bin", "fr.chiffre.ChiffreSolveur"], capture_output=True)

end = now()

print(res.stdout.decode())

print("temps de calcul java :", end - start)

print()

start = now()

res = run(["py", "solve.py", "-t", "4", "100", "6", "75", "8", "7", "573"], capture_output=True)

end = now()

print(res.stdout.decode())

print("temps de calcul python :", end - start)
