# A challenge from a friend, "make a function that multiplies a given integer by
# 217. You may not use arithmetic operators * / % + -"

# I didn't know if there was some clever way to do it so I just made code to mulitply
# any two numbers in general

def add_bit(x, y, bit, carry):
    """Adds a single bit of a number, for example, 0b_1_000 and 0b_0_000 (the fourth bit)"""
    if x & y:  # 1 & 1
        if carry:  # (1) + 1 + 1 = 11 (will carry)
            return x & y, True  # 01, carry=True
        else:  # (0) + 1 + 1 = 10 (will carry)
            return 0b0, True  # 00, carry=True

    elif x | y:  # 1 | 0
        if carry:  # (1) + 1 + 0 = 10 (will carry)
            return 0b0, True  # 00, carry=True
        else:  # (0) + 1 + 0 = 01 (no carry)
            return x | y, False  # 01, carry=False

    else:  # 0 | 0
        if carry:  # (1) + 0 + 0 = 01 (no carry)
            return bit, False  # bit is like 0b1000 or whatever bit we're currently on, carry=False
        else:  # (0) + 0 + 0 = 00 (no carry)
            return 0b0, False  # 00, carry=False


def add(a, b):
    """Adds two numbers like 0b1010 and 0b1110"""
    result = 0b0  # starts at 0, will add to later
    carry = False  # will signify whether next bit addition needs to include a carried 1
    for n in range(50):  # assuming numbers being added are only 50 binary digits long, can be arbitrarily increased
        bit = 0b1 << n  # 0b1, 0b10, 0b100, 0b1000, ...
        a_bit = a & bit  # for example, if a = 0b1111 and bit=0b100, a_bit = 0b0100
        b_bit = b & bit  # if b = 0b0001 and bit=0b100, b_bit = 0b0000
        add_bit_result, carry = add_bit(a_bit, b_bit, bit, carry)
        result = result | add_bit_result  # example, 0b0010 | 0b0100 = 0b0110

        # print(f"{bin(bit)=}, {bin(a & bit)=} + {bin(b & bit)=} = {bin(add_bit(a & bit, b & bit, bit, carry)[0])} "
        # f"--> {bin(result)}")
    # print(f"Answer: {bin(a+b)}")
    return result


def multiply(a, b):
    """Multiplies two numbers using shift add multiplication"""
    result = 0b0  # starts at 0, will add to later
    for n in range(50):  # assuming numbers being added are only 50 binary digits long, can be arbitrarily increased
        bit = 0b1 << n  # 0b1, 0b10, 0b100, 0b1000, ...
        # a_bit = a & bit  # for example, if a=0b1111 and bit=0b100, a_bit = 0b0100
        b_bit = b & bit  # if b=0b0001 and bit=0b100, b_bit = 0b0000
        if b_bit:
            result = add(result, a << n)
    return result


print(multiply(3, 7))  # 21
print(multiply(4, 8))  # 32
print(multiply(23, 11))  # 253
print(multiply(53, 217))  # 11501

