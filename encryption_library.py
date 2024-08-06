from random import randint

def is_prime(n):
    if n < 2:
        return False
    for i in range(2,n):
        if n % i == 0:
            return False
    return True

#calculates the totient of two numbers
def totient(x, y):
    return (x-1)*(y-1)


#returns all coprimes of a given number
def coprimes(n):
    n2 = 2
    n_coprimes = []
    while n2 < n:
        coprime = True
        for i in range(2,n2+1):
            if n2 % i == 0 and n % i == 0:
                coprime = False
        if coprime == True:
            n_coprimes.append(n2)
        n2 += 1
    return n_coprimes


#returns the greatest common divisor of two numbers
def gcd(a, b):
    gcd = 1
    for i in range(1,a+1):
        #checks if i is a common factor of a and b
        if a % (i) == 0 and b % (i) == 0:
            gcd = i
    return gcd


#finds two numbers that satisfy bezout's theorem and returns the largest
def D(t, e, n):
    
    GCD = gcd(t, e)
    t_multiples = []
    e_multiples = []
    
    count = 0
    while True:
        count += 1
        t_multiples.append(t*count)
        e_multiples.append(e*count)
        
        for i in range(count):

            #checks if there are any combinations of multiples of x and y that satisfy bezout's theorem
            
            if t_multiples[count-1] + (e_multiples[i] * -1) == GCD:
                d = int(t_multiples[count-1] / t)
                if d != 1:
                    return d

            elif t_multiples[i] + (e_multiples[count-1] * -1) == GCD:
                d = int(t_multiples[i] / t)
                if d != 1:
                    return d

            elif (t_multiples[count-1] * -1) + e_multiples[i] == GCD:
                d = int(e_multiples[i] / e)
                if d != 1:
                    return d

            elif (t_multiples[i] * -1) + e_multiples[count-1] == GCD:
                d = int(e_multiples[count-1] / e)
                if d != 1:
                    return d


def transform(text, key): #encrypts/decrypts a given string with a given key
    if key == (0,0): #this means no key was entered and no messages are being ecrypted
        return text
    
    newtext = ""
    character = ""
    for i in text: #encrypts/decrypts each character using the given key
        character = i
        character = ord(character)
        character = (character ** key[1]) % key[0]
        character = chr(character)
        newtext += character
        
    return newtext

