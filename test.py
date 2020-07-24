def validNumber(numAsString):
        if numAsString == "all":
            return True
            
        try:
            val = int(numAsString)
            assert val > 0
            return True
        except:
            return False

n1 = "all"
n2 = "12"
n3 = "-1"
n4 = "1.5"

print("input: " + n1 + ", valid: "+ str(validNumber(n1)))
print("input: " + n2 + ", valid: "+ str(validNumber(n2)))
print("input: " + n3 + ", valid: "+ str(validNumber(n3)))
print("input: " + n4 + ", valid: "+ str(validNumber(n4)))
