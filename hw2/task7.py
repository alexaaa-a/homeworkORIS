# Напишите программу, которая разбивает текстовый файл на
# равные части и использует потоки для параллельного подсчета частоты
# каждого слова. В конце нужно объединить результаты из всех потоков и
# вывести итоговую статистику.


from concurrent.futures import ThreadPoolExecutor


def count_words(part):
    part_counts = {}
    for i in part:
        if i.lower() not in part_counts:
            part_counts[i.lower()] = 1
        else:
            part_counts[i.lower()] += 1

    return part_counts


f = open("text.txt", encoding='utf-8').read().splitlines()
words = []
for i in f:
    word = ''
    for j in i:
        if j == ' ' and word != '':
            words.append(word)
            word = ''
        elif j.isalpha() or j.isdigit():
            word += j
        else:
            continue

n = int(input("Введите количество потоков для подсчета частоты каждого слова в тексте: "))
parts = len(words) // n
parts_words = [words[i:i + parts] for i in range(0, len(words), parts)]
max_workers = 5

counts = {}

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    results = [executor.submit(count_words, i) for i in parts_words]
    for i in results:
        part_counts = i.result()
        for word, num in part_counts.items():
            if word in counts:
                counts[word] += num
            else:
                counts[word] = num

for word, num in sorted(counts.items(), key=lambda x: x[1], reverse=True):
    print(f"{word}: {num}")
