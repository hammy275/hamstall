def get_input(question, options, default):
    """input() but supports a default answer and
    makes sure input is acceptable"""
    answer = "This is a string. There are many others like it, but this one is mine." #Set answer to something
    while answer not in options and answer != "":
        answer = input(question)
        answer = answer.lower() #Loop ask question while the answer is invalid or not blank
    if answer == "":
        return default #If answer is blank return default answer
    else:
        return answer #Return answer if it isn't the default answer