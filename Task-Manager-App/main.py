user_text = input("Enter to do")
print(user_text)
user_text = int(user_text)
nums = []
for i in range(user_text):
    val = int(input("Enter a number"))
    nums.append(val)

print(nums)
print(type(nums))