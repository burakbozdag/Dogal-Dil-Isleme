import spacy

nlp = spacy.load('en_core_web_md') # en_core_web_sm is smaller but less accurate


# Öğrenciler, aldıkları dersler ve notlarının tutulduğu veri yapısı
students = {
    "Burak": {
        "Natural Language Processing": 90,
        "Maths": 80,
        "English": 70
    }
}

def student_grade_query(student:str, course:str):
    try:
        print(student, "took", str(students[student][course]), "from", course, "course.")
        return True
    except:
        print(student, "does have no grade from", course, "course.")
        return False

def student_grade_entry(student:str, course:str, grade:int):
    if student not in students:
        students[student] = {}
    try:
        students[student][course] = grade
        print("The grade", str(grade), "for the course", course, "is recorded for the student", student, "successfully.")
        return True
    except:
        print("An error occurred when recording grade!")
        return False

enter_words = [
    "enter",
    "give",
    "entry"
]
query_words = [
    "query",
    "learn",
    "know",
    "get",
    "see"
]
enter_nlp = [nlp(w) for w in enter_words]
query_nlp = [nlp(w) for w in query_words]

while True:
    sentence = input("\nWhat do you want to do? (querying or entering student grades, 0 to exit, 1 to see all students' data)\n").strip()

    if sentence == "0":
        break
    if sentence == "1":
        for s in students:
            print(s + ":")
            for c in students[s]:
                print("\t", c + ":", str(students[s][c]))
        continue
    
    doc = nlp(sentence)

    student = None
    course = None
    grade = None
    is_entry = False # Query or entry sentence

    #print("Entities:")
    for ent in doc.ents:
        if ent.label_ == "PERSON": # Kiminle alakalı konuşulduğu bulunur.
            student = ent.text
        elif ent.label_ in ["ORG", "WORK_OF_ART", "GPE"]: # Ders ismi bulunur.
            course = ent.text
        elif ent.label_ in ["CARDINAL"]: # Girilecek not bulunur.
            grade = int(ent.text)
        #print(ent.text, ent.label_)
    
    enter_prob = 0.0
    query_prob = 0.0
    #print("PoS Tags:")
    for token in doc:
        if token.is_stop: #token.is_alpha
            continue

        if grade is not None:
            is_entry = True # Not yazdığı için kesinlikle entry cümlesidir.
            break
        
        if token.pos_ in ["NUM"]: # Entity olarak bulunamayan not değeri PoS tag aracılığıyla bulunur.
            grade = int(token.text)
            is_entry = True # Not yazdığı için kesinlikle entry cümlesidir.
            break
        
        for e in enter_nlp:
            prob = e.similarity(token)
            if prob > enter_prob:
                enter_prob = prob
        
        for q in query_nlp:
            prob = q.similarity(token)
            if prob > query_prob:
                query_prob = prob

        #print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_)
    
    if not is_entry and enter_prob > query_prob:
        is_entry = True # Entry sentence confirmed
    
    # Eksik parametrelere göre kullanıcıdan istenecek bilgiler
    if student is None:
        student = input("Enter the name of the student: ").strip()
    if course is None:
        course = input("Enter the name of the course: ").strip()
    if grade is None and is_entry:
        grade = input("Enter the grade of " + student + " for the " + course + " course: ").strip()
        try:
            grade = int(grade)
        except:
            print("Grade is invalid.")
            continue

    if is_entry: # Not girişi
        student_grade_entry(student, course, grade)
    else: # Not sorgulama
        student_grade_query(student, course)
    
    print("--------------------------------------------------------------------")
