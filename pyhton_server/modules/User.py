class User():
    def __init__(self, name, gender, surname, date_of_birth, city, region, 
                 hobby1, hobby2, hobby3, category1, category2, category3, sub_category1, sub_category2, sub_category3):
        self.name = name
        self.surname = surname
        self.city = city
        self.region = region
        self.hobby1 = hobby1
        self.hobby2 = hobby2
        self.hobby3 = hobby3
        self.category1 = category1
        self.category2 = category2
        self.category3 = category3
        self.sub_category1 = sub_category1
        self.sub_category2 = sub_category2
        self.sub_category3 = sub_category3
        self.gender = gender
        self.date_of_birth = date_of_birth


    def __str__(self):
        #for debugging
        return f"{self.name},{self.surname},{self.gender}"


