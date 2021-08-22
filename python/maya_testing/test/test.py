def impossible_math(num):
    if num % 2 == 0:
        result = num / 2
        # print("number is even: " + str(num))
        return result
    else:
        result = (num * 3) + 1
        # print("number is odd: " + str(num))
        return result


if __name__ == '__main__':
    # num = 700
    for i in range(1, 70000000):
        num = i
        counter = 0
        while num != 1:
            num = impossible_math(num)
            counter += 1

        if num == 1:
            print (counter, i)

