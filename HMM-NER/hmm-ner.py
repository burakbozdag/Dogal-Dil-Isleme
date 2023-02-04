# Burak Bozdağ
# 504211552

# Sözlükler
train = {}
test  = {}

# Dosya okuma
train_dosya = open("milliyet-ner/train.txt", mode="r", encoding="utf8")
test_dosya  = open("milliyet-ner/test.txt" , mode="r", encoding="utf8")

sayac = 0
# Train
train_etiketli_kelimeler = [["", "Start"]] # Birazdan A matrisinin hesaplanmasında kullanılacak.
satirlar = train_dosya.readlines()
for satir in satirlar:
    splitted = satir.split(" ")
    if len(splitted) == 1: # Boş satır (cümle sonu)
        train_etiketli_kelimeler.append(["", "End"])
        train_etiketli_kelimeler.append(["", "Start"]) # Başka bir cümle başlayacağı için ekleniyor.
        continue
    sayac += 1
    kelime = splitted[0].casefold()
    etiket = splitted[1].strip()
    train_etiketli_kelimeler.append([kelime, etiket])
    try:
        len(train[etiket]) # Etiket mevcut mu diye bakılır.
    except Exception:
        train[etiket] = {}
    try:
        train[etiket][kelime] += 1 # Kelime sayacı arttırılır.
    except Exception:
        train[etiket][kelime] = 1 # Bu etiketteki kelimeye ilk defa rastlanmıştır.
train_etiketli_kelimeler.pop() # En son eklenen cümle başı etiketi silinir.
print("Train kelime sayisi: ", sayac)
#######

sayac = 0
# Test
test_etiketli_kelimeler = [["", "Start"]]
satirlar = test_dosya.readlines()
for satir in satirlar:
    splitted = satir.split(" ")
    if len(splitted) == 1: # Boş satır (cümle sonu)
        test_etiketli_kelimeler.append(["", "End"])
        test_etiketli_kelimeler.append(["", "Start"]) # Başka bir cümle başlayacağı için ekleniyor.
        continue
    sayac += 1
    kelime = splitted[0].casefold()
    etiket = splitted[1].strip()
    test_etiketli_kelimeler.append([kelime, etiket])
    try:
        len(test[etiket]) # Etiket mevcut mu diye bakılır.
    except Exception:
        test[etiket] = {}
    try:
        test[etiket][kelime] += 1 # Kelime sayacı arttırılır.
    except Exception:
        test[etiket][kelime] = 1 # Bu etiketteki kelimeye ilk defa rastlanmıştır.
test_etiketli_kelimeler.pop() # En son eklenen cümle başı etiketi silinir.
print("Test kelime sayisi: ", sayac)
#######

# A (transition) ve B (emission) matrislerinin hesaplanması
# A: etiketten sonra diğer etiketlerin gelme olasılıkları (N+1 x N+1) +1 satır ve sütun sırasıyla start ve end state'leri içindir.
# B: etiketin belirli bir kelime olma olasılıkları (W x N)

etiketler = []
for key in train.keys():
    if key not in etiketler:
        etiketler.append(key)
print("Etiketler", etiketler)

kelimeler = []
for value in train.values():
    for kelime in value.keys():
        kelimeler.append(kelime)
print("Farkli kelime sayisi: ", len(kelimeler))

B = []
for etiket in etiketler:
    B.append([])
    for kelime in kelimeler:
        try:
            B[-1].append(train[etiket][kelime])
        except Exception:
            B[-1].append(0)
print("B: ", len(B), "x", len(B[0]))
# B matrisinin olasılık değerleri atanır.
for i in range(len(B)):
    sum = 0
    for j in range(len(B[i])):
        sum += B[i][j]
    for j in range(len(B[i])):
        B[i][j] /= sum

A = []
for e1 in range(len(etiketler) + 1):
    A.append([])
    for e2 in range(len(etiketler) + 1):
        A[-1].append(0)
for i in range(len(train_etiketli_kelimeler) - 1):
    try:
        e1 = etiketler.index(train_etiketli_kelimeler[i][1])
    except Exception:
        e1 = len(etiketler) # Start
    try:
        e2 = etiketler.index(train_etiketli_kelimeler[i + 1][1])
    except Exception:
        e2 = len(etiketler) # End
    A[e1][e2] += 1
print("A: ", len(A), "x", len(A[0]))

# A matrisinin olasılık değerleri atanır.
for i in range(len(A)):
    sum = 0
    for j in range(len(A[i])):
        sum += A[i][j]
    for j in range(len(A[i])):
        A[i][j] /= sum

#######
# Artık elimizde A ve B matrisleri var.
# Viterbi algoritmasını kullanarak sınama yapabiliriz.

def sinama_viterbi(cumle, A_transition, B_emission, etiketler, verbose=False):
    V = [{}] # Viterbi çıktısı

    for e in etiketler:
        try:
            V[0][e] = {
                "olasilik": A_transition[len(etiketler)][etiketler.index(e)] * B_emission[etiketler.index(e)][kelimeler.index(cumle[0][0])],
                "onceki"  : None
                }
        except Exception: # Kelime bulunamadı, olasılığımız burada 0 oluyor.
            V[0][e] = {
                "olasilik": 0,
                "onceki"  : None}

    # Sonraki etiketler için ana Viterbi algoritması çalışmaya devam eder.
    for t in range(1, len(cumle)):
        V.append({})

        for e in etiketler:
            secilen_onceki_etiket = etiketler[0]
            max_mevcut_olasilik = V[t - 1][etiketler[0]]["olasilik"] * A_transition[0][etiketler.index(e)]

            for onceki_etiket in etiketler[1:]:
                try:
                    mevcut_olasilik = V[t - 1][etiketler.index(onceki_etiket)]["olasilik"] * A_transition[etiketler.index(onceki_etiket)][etiketler.index(e)]
                except Exception: # Kelime bulunamadı, olasılığımız burada 0 oluyor.
                    mevcut_olasilik = 0

                if mevcut_olasilik > max_mevcut_olasilik: # Hesaplanan olasılık max. olandan fazla ise seçeriz.
                    max_mevcut_olasilik   = mevcut_olasilik
                    secilen_onceki_etiket = onceki_etiket

            try:
                max_olasilik = max_mevcut_olasilik * B_emission[etiketler.index(e)] [kelimeler.index(cumle[t][0])]
            except Exception: # Kelime bulunamadı, olasılığımız burada 0 oluyor.
                max_olasilik = 0

            V[t][e] = {
                "olasilik": max_olasilik,
                "onceki"  : secilen_onceki_etiket
                }

    max_olasilik      = 0.0
    optimum_etiketler = []
    en_olasi_etiket   = None

    # En olası seçenek bulunur.
    for e, veriler in V[-1].items():
        if veriler["olasilik"] > max_olasilik:
            en_olasi_etiket = e
            max_olasilik    = veriler["olasilik"]

    onceki = en_olasi_etiket

    if en_olasi_etiket is None: # Sonuç 0 geldiyse tahmin yapamıyoruz, her eleman için "O" etiketi atanıyor.
        optimum_etiketler.append("O")
        for i in range(len(V) - 2, -1, -1):
            optimum_etiketler.insert(0, "O")
    else: # En olası seçenekten geriye doğru yol izlenir.
        optimum_etiketler.append(en_olasi_etiket)
        for i in range(len(V) - 2, -1, -1):
            optimum_etiketler.insert(0, V[i + 1][onceki]["onceki"])
            onceki = V[i + 1][onceki]["onceki"]

    if verbose:
        print(cumle, ": " + ", ".join(optimum_etiketler))
        print("Maksimum olasilik:", max_olasilik)
    
    return optimum_etiketler

#######

# Sınama aşaması, test veri kümesi içindeki cümleler üzerinde sinama_viterbi fonksiyonu ile tahmin yürütülür.
dogru_sayisi  = 0
yanlis_sayisi = 0

sinanacak_cumle_kelimeleri = []
sinanacak_cumle_etiketleri = []
for ek in test_etiketli_kelimeler:
    kelime = ek[0]
    etiket = ek[1]

    if etiket == "Start":
        continue
    if etiket == "End":
        etiket_tahminleri = sinama_viterbi(sinanacak_cumle_kelimeleri, A, B, etiketler)
        for t in range(len(etiket_tahminleri)):
            if etiket_tahminleri[t].split("-")[-1] == sinanacak_cumle_etiketleri[t].split("-")[-1]: # beginning-inside fark etmeksizin etiket doğruysa sorun yoktur.
                dogru_sayisi +=1
            else:
                yanlis_sayisi += 1
        
        # Sınanacak yeni cümleler için listeler sıfırlanır.
        sinanacak_cumle_kelimeleri = []
        sinanacak_cumle_etiketleri = []
        continue
    
    sinanacak_cumle_kelimeleri.append(kelime)
    sinanacak_cumle_etiketleri.append(etiket)

print("Dogru sayisi:" , dogru_sayisi )
print("Yanlis sayisi:", yanlis_sayisi)

print("F1 skoru:", dogru_sayisi / (dogru_sayisi + yanlis_sayisi))