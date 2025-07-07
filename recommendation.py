

questions = {1: "Как часто вы испытываете ощущение сухости на вашем лице?\n",
 2: "Как ваша кожа реагирует на обычное мыло?\n",
 3: "Как часто вы замечаете блеск или жирный блеск на вашем лице?\n",
 4: "Как ваша кожа реагирует на изменения погоды, такие как холод или влажность?\n",
 5: "Как вы оцениваете состояние пор на вашем лице?\n",
 6: "Как вы оцениваете уровень упругости вашей кожи?\n",
 7: "Сколько часов вы в среднем спите?\n",
 8: "Какой уровень SPF предпочитаете для солнцезащиты?\n",
 9: "Есть ли у вас какие-либо аллергии или чувствительность к определенным ингредиентам?\n",
 10: "Какие проблемы с кожей вас беспокоят? (можно выбрать несколько вариантов)\n",
}

answers = {1: "1 - Почти никогда\n"
 "2 - Иногда, особенно после мытья\n"
 "3 - Часто, моя кожа постоянно чувствует сухость\n",
 2: "1 - Она обычно остается мягкой и увлажненной\n"
 "2 - Она становится немного сухой и стянутой\n"
 "3 - Она становится сухой и раздраженной\n",
 3: "1 - Почти никогда\n"
 "2 - Иногда, особенно в течение дня\n"
 "3 - Часто, моя кожа постоянно выглядит жирной\n",
 4: "1 - Она обычно не реагирует или реагирует слабо\n"
 "2 - Она становится немного сухой или раздраженной\n"
 "3 - Она реагирует сильно, меняя текстуру или высыпаниями\n",
 5: "1 - Они мало заметны и не вызывают проблем\n"
 "2 - Они видны, но не вызывают беспокойства\n"
 "3 - Они заметны и порой забиты, вызывая проблемы с чистотой кожи\n",
 6: "1 - Она обычно кажется упругой и эластичной\n"
 "2 - Она немного утратила упругость, но еще не слишком заметно\n"
 "3 - Она потеряла значительную упругость, появились морщины или провисание\n",
 7: "1 - Менее 4 часов в день\n"
 "2 - 5-6 часов в день\n"
 "3 - 8 часов и более\n",
 8: "1 - SPF 15-30\n"
 "2 - SPF 30-50\n"
 "3 - SPF 50+\n"
 "4 - Я предпочитаю косметику без SPF\n",
 9: "1 - Да\n"
 "2 - Нет\n",
 10: "1 - Акне/прыщи\n"
 "2 - Пигментные пятна\n"
 "3 - Повышенная чувствительность\n"
 "4 - Морщины/старение кожи\n"
 "5 - Раздражение\n"
 "6 - Нет проблем, хочу поддерживать здоровье кожи\n",
}

# блоки правил: для сухой, для жирной, для комби, для нормальной, для возрастной

from experta import *
from celery_config import app


class SkinCareExpert(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        # Меры доверия
        self.dry = 0
        self.oily = 0
        self.combined = 0
        self.normal = 0

        # Меры недоверия
        self.mnd_dry = 0
        self.mnd_oily = 0
        self.mnd_combined = 0
        self.mnd_normal = 0

        self.acne = 0
        self.pigmented = 0
        self.sensitive = 0
        self.wrinkles = 0
        self.puffy = 0
        self.none = 1

    # Веса вопросов
    weights = {
        1: 0.2,
        2: 0.15,
        3: 0.3,
        4: 0.1,
        5: 0.05,
        6: 0.1,
        7: 0.05,
        8: 0.03,
        9: 0.02,
        10: 0.1
    }

    @Rule(
        Fact(answ="1-3") | Fact(answ="2-3") | Fact(answ="4-2"))
    def plusDry(self):
        weight_1 = self.weights[1]
        weight_2 = self.weights[2]
        weight_4 = self.weights[4]
        self.dry += (0.5 * weight_1) * (1 - self.dry)
        self.mnd_oily += (0.5 * weight_2) * (1 - self.mnd_oily)
        self.mnd_combined += (0.5 * weight_4) * (1 - self.mnd_combined)
        self.mnd_normal += (0.5 * weight_4) * (1 - self.mnd_normal)

    @Rule(
        Fact(answ="3-3") | Fact(answ="5-3"))
    def plusOily(self):
        weight_3 = self.weights[3]
        weight_5 = self.weights[5]
        self.oily += (0.19 * weight_3) * (1 - self.oily)
        self.mnd_dry += (0.19 * weight_5) * (1 - self.mnd_dry)
        self.mnd_combined += (0.19 * weight_3) * (1 - self.mnd_combined)
        self.mnd_normal += (0.19 * weight_5) * (1 - self.mnd_normal)

    @Rule(
        Fact(answ="1-2") | Fact(answ="2-2") | Fact(answ="3-2") | Fact(answ="4-1"))
    def plusCombined(self):
        weight_1 = self.weights[1]
        weight_2 = self.weights[2]
        weight_3 = self.weights[3]
        weight_4 = self.weights[4]
        self.combined += (0.63 * weight_3) * (1 - self.combined)
        self.mnd_oily += (0.63 * weight_2) * (1 - self.mnd_oily)
        self.mnd_dry += (0.63 * weight_1) * (1 - self.mnd_dry)
        self.mnd_normal += (0.63 * weight_4) * (1 - self.mnd_normal)

    @Rule(
        Fact(answ="1-1") | Fact(answ="2-1") | Fact(answ="3-1") | Fact(answ="4-1") | Fact(answ="5-1") | Fact(answ="6-1"))
    def plusNormal(self):
        weight_1 = self.weights[1]
        weight_2 = self.weights[2]
        weight_3 = self.weights[3]
        weight_4 = self.weights[4]
        weight_5 = self.weights[5]
        weight_6 = self.weights[6]
        self.normal += (0.72 * weight_1) * (1 - self.normal)
        self.mnd_oily += (0.72 * weight_2) * (1 - self.mnd_oily)
        self.mnd_combined += (0.72 * weight_3) * (1 - self.mnd_combined)
        self.mnd_dry += (0.72 * weight_6) * (1 - self.mnd_dry)

    @Rule(
        Fact(answ="4-3") | Fact(answ="6-3") | Fact(answ="7-1") | Fact(answ="8-4") | Fact(answ="9-1"))
    def problematic(self):
        weight_4 = self.weights[4]
        weight_6 = self.weights[6]
        weight_7 = self.weights[7]
        weight_8 = self.weights[8]
        weight_9 = self.weights[9]
        self.dry += (0.2 * weight_4) * (1 - self.dry)
        self.oily += (0.32 * weight_6) * (1 - self.oily)
        self.combined += (0.3 * weight_8) * (1 - self.combined)
        self.normal += (0.1 * weight_9) * (1 - self.normal)

    @Rule(
        Fact(answ="6-2") | Fact(answ="7-2") | Fact(answ="8-1"))
    def mediumProblematic(self):
        weight_6 = self.weights[6]
        weight_7 = self.weights[7]
        weight_8 = self.weights[8]
        self.dry += (0.05 * weight_7) * (1 - self.dry)
        self.oily += (0.02 * weight_8) * (1 - self.oily)
        self.combined += (0.05 * weight_6) * (1 - self.combined)
        self.normal += (0.1 * weight_6) * (1 - self.normal)

    @Rule(
        Fact(answ="7-3") | Fact(answ="8-2") | Fact(answ="8-3") | Fact(answ="9-2"))
    def goodCare(self):
        weight_7 = self.weights[7]
        weight_8 = self.weights[8]
        weight_9 = self.weights[9]
        self.dry += (0.1 * weight_7) * (1 - self.dry)
        self.oily += (0.1 * weight_9) * (1 - self.oily)
        self.combined += (0.2 * weight_8) * (1 - self.combined)

    @Rule(
        Fact(answ="10-1"))
    def acne(self):
        self.acne += 1
        self.none = 0

    @Rule(
        Fact(answ="10-2"))
    def pigmented(self):
        self.pigmented += 1
        self.none = 0

    @Rule(
        Fact(answ="10-3"))
    def sens(self):
        self.sensitive += 1
        self.none = 0

    @Rule(
        Fact(answ="10-4"))
    def old(self):
        self.wrinkles += 1
        self.none = 0

    @Rule(
        Fact(answ="10-5"))
    def puffy(self):
        self.puffy += 1
        self.none = 0

    def get_certainty_factors(self):
        return {
            'Oily': self.oily - self.mnd_oily,
            'Dry': self.dry - self.mnd_dry,
            'Normal': self.normal - self.mnd_normal,
            'Combined': self.combined - self.mnd_combined
        }

    def get_specific_conditions(self):
        return {
            'acne': self.acne,
            'none': self.none,
            'pigm': self.pigmented,
            'sens': self.sensitive,
            'wrinkles': self.wrinkles,
            'irritated': self.puffy
        }

    def checkSkincare(self):
        ku = self.get_certainty_factors()
        spec = self.get_specific_conditions()
        print(ku)
        print(spec)
        max_type = max(ku, key=ku.get)
        max_conditions = [k for k, v in spec.items() if v == 1 and k != 'none']

        print(f"Рекомендуемый тип ухода: {max_type}")
        if max_conditions:
            print(f"Обратите внимание на продукты для: {', '.join(max_conditions)}")
        return (max_type, max_conditions)

@app.task
def calculate_skin_type(answers):
    expert = SkinCareExpert()
    expert.reset()

    for question_id, answer in answers.items():
        expert.declare(Fact(answ=f"{question_id}-{answer}"))

    expert.run()

    # Получаем тип кожи и состояния кожи
    skin_types, conditions = expert.get_certainty_factors(), expert.get_specific_conditions()

    # Находим тип кожи с наибольшим значением
    best_skin_type = [max(skin_types, key=skin_types.get)]

    # Выбираем состояния, у которых значение == 1
    active_conditions = [cond for cond, value in conditions.items() if value == 1]

    return best_skin_type, active_conditions


def collect_user_answers():
    questions = {
        1: "Как часто вы испытываете ощущение сухости на вашем лице?\n"
           "1 - Почти никогда\n"
           "2 - Иногда, особенно после мытья\n"
           "3 - Часто, моя кожа постоянно чувствует сухость\n",
        2: "Как ваша кожа реагирует на обычное мыло?\n"
           "1 - Она обычно остается мягкой и увлажненной\n"
           "2 - Она становится немного сухой и стянутой\n"
           "3 - Она становится сухой и раздраженной\n",
        3: "Как часто вы замечаете блеск или жирный блеск на вашем лице?\n"
           "1 - Почти никогда\n"
           "2 - Иногда, особенно в течение дня\n"
           "3 - Часто, моя кожа постоянно выглядит жирной\n",
        4: "Как ваша кожа реагирует на изменения погоды, такие как холод или влажность?\n"
           "1 - Она обычно не реагирует или реагирует слабо\n"
           "2 - Она становится немного сухой или раздраженной\n"
           "3 - Она реагирует сильно, меняя текстуру или высыпаниями\n",
        5: "Как вы оцениваете состояние пор на вашем лице?\n"
           "1 - Они мало заметны и не вызывают проблем\n"
           "2 - Они видны, но не вызывают беспокойства\n"
           "3 - Они заметны и порой забиты, вызывая проблемы с чистотой кожи\n",
        6: "Как вы оцениваете уровень упругости вашей кожи?\n"
           "1 - Она обычно кажется упругой и эластичной\n"
           "2 - Она немного утратила упругость, но еще не слишком заметно\n"
           "3 - Она потеряла значительную упругость, появились морщины или провисание\n",
        7: "Сколько часов вы в среднем спите?\n"
           "1 - Менее 4 часов в день\n"
           "2 - 5-6 часов в день\n"
           "3 - 8 часов и более\n",
        8: "Какой уровень SPF предпочитаете для солнцезащиты?\n"
           "1 - SPF 15-30\n"
           "2 - SPF 30-50\n"
           "3 - SPF 50+\n"
           "4 - Я предпочитаю косметику без SPF\n",
        9: "Есть ли у вас какие-либо аллергии или чувствительность к определенным ингредиентам?\n"
           "1 - Да\n"
           "2 - Нет\n",
        10: "Какие проблемы с кожей вас беспокоят? (можно выбрать несколько вариантов, через запятую)\n"
            "1 - Акне/прыщи\n"
            "2 - Пигментные пятна\n"
            "3 - Повышенная чувствительность\n"
            "4 - Морщины/старение кожи\n"
            "5 - Раздражение\n"
            "6 - Нет проблем, хочу поддерживать здоровье кожи\n",
    }

    answers = {}
    for question_id, question_text in questions.items():
        print(question_text)
        user_input = input("Ваш ответ: ").strip()
        if question_id == 10:  # Если это вопрос с несколькими ответами
            answers[question_id] = user_input.split(",")
        else:
            answers[question_id] = user_input
    return answers

