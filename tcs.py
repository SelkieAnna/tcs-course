def main():
    input = [1, 0, 1, 0, 0, 1, 1, 0, 1]
    check(0, input)

def check(q, inp):
    if inp == []:
        if q == 0:
            print("Accepted")
        else:
            print("Not Accepted")
    else:
        i = inp.pop()
        check(state(q, i), inp)

def state(q, inp):
    if q == 0:
        if inp == 0:
            return 0
        elif inp == 1:
            return 1
    elif q == 1:
        if inp == 0:
            return 2
        elif inp == 1:
            return 0
    elif q == 2:
        if inp == 0:
            return 1
        elif inp == 1:
            return 2

if __name__ == '__main__':
    main()