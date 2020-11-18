from edufinder.rest_api.models import UserAnswer, Answer, AnswerChoice, Question, Education
import math




def CreateQuestionTree():
    print("Fetching data")
    userAnswers = FetchUserAnswers()
    questions = list(Question.objects.all())
    educations = list(Education.objects.all())


    print("Creating tree")
    tree = CreateBranch(userAnswers, questions, educations)
    tree.print_tree()



def CreateBranch(userAnswers, questions, educations, nodeChoice = None):
    left = len(questions)
    dataC = len(userAnswers)
    if left == 0 or dataC == 0:
        return None

    print("Questions left " + str(left) + " with " +str(dataC) + " entries")

    question = FindLocalBestQuestion(userAnswers, questions, educations)

    node = Node(question, nodeChoice)

    questions.remove(question)
    for choice in AnswerChoice:
        dataSet = GetWhere(userAnswers, question, choice)
        print(len(dataSet))

        child = CreateBranch(dataSet, questions.copy(), educations, choice)

        if child is not None:
            node.add_child(child)
    return node
    
#Should return all userAnswers where the question == choice
def GetWhere(userAnswers, question, choice):
    result = {}
    for answer in userAnswers:
        if question in userAnswers[answer]:
            if userAnswers[answer][question].answer == choice:
                result[answer] = userAnswers[answer]
    return result



    

def FindLocalBestQuestion(userAnswers, questions, educations):
    bestQuestion = questions[0]
    bestGain = CalculateGain(userAnswers, questions[0], educations)
    print("first gain")
    for i in range(1, len(questions)):
        gain = CalculateGain(userAnswers, questions[i], educations)
        if gain < bestGain:
            bestQuestion = questions[i]
            bestGain = gain

    return bestQuestion




def CalculateEntropy(userAnswers, educations):
    sum = 0
    for education in educations:
        px = ProportionIsOfClass(userAnswers, education)
        if px == 0:
            continue
        else:
            sum += -px * math.log2(px)
    return sum

def ProportionIsOfClass(userAnswers, education):
    count = len(userAnswers)
    inClassCount = 0
    for answer in userAnswers.keys():
        if answer.education == education:
            inClassCount += 1

    if count == 0:
        return 0

    return inClassCount / count

def ProportionOfSubset(userAnswers, subset):
    return len(subset) / len(userAnswers)



def CalculateGain(userAnswers, question, educations):
    sum = 0
    T = {}
    for choice in AnswerChoice:
        T[choice] = {}

        for userAnswer in userAnswers:
            if question in userAnswers[userAnswer]:
                T[choice][userAnswer] = userAnswers[userAnswer]

    sum += ProportionOfSubset(userAnswers, T[choice]) * CalculateEntropy(T[choice], educations)
    

    return CalculateEntropy(userAnswers, educations) - sum

def FetchUserAnswers():
    userAnswers = {}
    answers = Answer.objects.all()

    #Populate useranswers with data
    for answer in answers:
        userAnswer = answer.userAnswer

        if userAnswer not in userAnswers:
            userAnswers[userAnswer] = {}
            userAnswers[userAnswer][answer.question] = answer
        else:
            userAnswers[userAnswer][answer.question] = answer
    
    return userAnswers
    
    

class Node:
    "Generic tree node."
    def __init__(self, question, choice = None, children=None):
        self.question = question
        self.children = []
        self.choice = choice
        if children is not None:
            for child in children:
                self.add_child(child)
    def __repr__(self):
        return self.question.question  

    def print_tree(self, prefix = ""):
        if self.choice is not None:
            print(prefix+self.choice + " into " + self.question.question)
        else:
            print(prefix+"root" + self.question.question)

        if self.children is not None:
            for child in self.children:
                child.print_tree(prefix+"--")

    def add_child(self, node):
        assert isinstance(node, Node)
        self.children.append(node)


def move (y, x):
    print("\033[%d;%dH" % (y, x))

