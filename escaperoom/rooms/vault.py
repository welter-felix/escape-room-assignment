#This is the raw version of the room logic, No Integrations with the rest of the game are included here SO FAR. 


#importing regex
import re



#  explanation: 
#
#We want to accept all Strings resembling this pattern "SAFE{A-B-C}" with the condition that the white spaces may vary
#
#In this regex, I mostly used "\s*" which just means there can be zero or more whitespaces in the expression
#
#The "^" marks the beginning of the expressing and after the "\s*" we check for the word SAFE, meaning if it would not be there, that line would not match
#
#then we check for the curly braces (which is a special character that is why I put a "\" in front of it just to make sure that it is seen as such)
#
#on the next stage I do 2 things, I use "()" which creates a group (so we can access the contents of it later) and with "\d" I specify that the string has to contain digits and with the "+" afterwards I make sure that it can be one or more digits
# 
# Then I repeat this process and I mark the end with "$"


#here i use re.compile so that the expression does no have to be compiled for each line
safe_pattern = re.compile(r'^\s*SAFE\s*\{\s*(\d+)\s*-\s*(\d+)\s*-\s*(\d+)\s*\}\s*$')

#import the file
f = open("data/vault_dump.txt")


# we iterate through each line in our file
for line in f:
    #here we look for patterns matching our regex
    match = safe_pattern.search(line)
    if match:
        #In case the regex matches we take the groups that we specified and see if a + b == c and if it matches we found our line
        if int(match.group(1)) + int(match.group(2))==int(match.group(3)):
            
            
            #Here I manually print the expected output format (this will all be modified later)
            print(f"TOKEN[SAFE]={match.group(1)}-{match.group(2)}-{match.group(3)}")
            print(f"EVIDENCE[SAFE].MATCH={line}",end="")
            print(f"EVIDENCE[SAFE].CHECK={match.group(1)}+{match.group(2)}={match.group(3)}")
                
        
        



