"""Captions per source clip, in source-clip seconds: CAP[path] = [[start, end, text], ...].

Hinglish lines are romanised from the Hindi-mode Whisper pass; lines spoken in English (or where the Hindi
pass only looped) follow the English pass. Lines nobody could make out are left uncaptioned on purpose.
"""
TR, GH, JU, GE = "travel/", "Guest House/", "Juhu Beach/", "General/"
EG, JI, MD, SH, CC = "Eth Global/", "Jio convection/", "Marine drive/", "shayari/", "Cat Cafe/"


def gx(folder, n):
    return f"{folder}GX0{n}_enhanced.mp4"


CAP = {
    # ---- departure, Bengaluru
    TR + "GX010075.MP4": [
        [0.3, 3.0, "Hey guys, toh hum jaa rahe hai ETH Hackathon pe"],
        [3.0, 7.3, "Abhi hum hackathon ke liye nikle hai — cab se, bus ke liye"],
        [7.3, 9.0, "Toh chalo, sab introduction dete hai"],
        [9.0, 12.9, "Pehle main Yash, aur ye meri team hai!"],
        [12.9, 14.6, "Hi bolo guys!"],
        [15.2, 16.5, "Ek ek karke introduction"],
        [16.55, 20.4, "Hello guys, mera naam hai Abhinav"],
        [20.45, 24.1, "Hum log ab chale bus stand ke liye — wahan Divija di humara wait kar rahi hai"],
        [24.13, 25.6, "Bye guys!"],
        [25.7, 27.9, "Hi guys, I am Soham"],
        [28.4, 31.2, "I am going with these two to do some hard work"],
        [34.9, 37.1, "Hi guys, I am Divyanshi"],
        [38.9, 40.3, "Wish us all the best!"],
        [43.3, 45.0, "So guys, keep watching our vlog"],
        [46.4, 49.0, "We're going to show you the whole journey of 5 days"],
        [49.2, 50.3, "Stay tuned!"],
        [50.4, 53.7, "Let's hope it goes well... let's see"],
        [53.9, 55.8, "If we win, let's have a party as well!"],
    ],
    TR + "GX010090.MP4": [
        [0.85, 4.1, "So guys, abhi hum bus stop pe wait kar rahe hai"],
        [5.4, 7.0, "Say hi, guys!"],
    ],
    TR + "GX010093.MP4": [
        [0.2, 4.6, "Toh guys, Mumbai gang ready ho chuki hai, aur bus bhi nikal chuki hai"],
        [4.64, 9.1, "So let's see once again — let me show you everyone"],
        [9.14, 12.5, "So this is Soham — our smart contract guy"],
        [12.5, 20.6, "He's made so many smart contracts that Ethereum is asking him to join"],
        [20.6, 23.3, "Vitalik will be there for sure, shaking his hand!"],
        [23.3, 27.5, "And this is our orchestration guy"],
        [27.5, 30.5, "This guy is just doing AI"],
        [30.8, 33.5, "And here are our two teammates"],
        [33.5, 35.3, "Can you introduce yourself?"],
        [35.3, 39.2, "I'm Divija... and Divyanshi!"],
    ],
    # ---- guest house
    gx(GH, 10117): [[1.9, 5.0, "Toh ye hamara guest house ka room hai, Abhinav bhai"]],
    gx(GH, 10123): [
        [0.0, 3.3, "So guys, we are ready — abhi hum hackathon ke liye jaane wale hai"],
        [3.4, 5.9, "Co-founder saab, are you ready?"],
        [6.4, 7.6, "Bilkul!"],
    ],
    gx(GH, 10142): [
        [0.85, 3.0, "Rate your excitement on a scale of 10!"],
        [3.0, 4.75, "10 on 10!"],
        [4.77, 7.1, "Rate your excitement on a scale of 10!"],
        [7.17, 7.87, "9 on 10"],
        [7.87, 9.6, "10 on 10!"],
        [9.6, 10.7, "10 on 10!"],
        [10.7, 12.2, "Let's go guys!"],
        [12.25, 14.1, "Sab log bahut excited hai"],
        [14.1, 16.6, "Let's see, hackathon mein kuch toh hoga..."],
        [16.6, 18.6, "Stay tuned!"],
    ],
    gx(GH, 10131): [
        [2.96, 8.2, "Guys, we are going to the dining hall in our guest house"],
        [8.2, 10.6, "...and this is it."],
    ],
    GH + "VID-20261108-WA0098.mp4": [
        [2.16, 5.3, "So guys, this is our room. We just got tea."],
        [5.3, 8.0, "Enjoy morning tea!"],
    ],
    gx(GH, 10273): [
        [3.1, 5.2, "Today we're leaving — it's the 8th"],
        [5.2, 9.1, "So before leaving, we'll show you our room — mine and Divija didi's"],
        [46.8, 49.8, "This is the view"],
        [49.8, 56.0, "Raat ko lights bahut achhi lagti hai"],
        [56.0, 61.8, "It looks so pretty"],
        [114.0, 117.0, "That is it. Bye-bye!"],
        [117.0, 120.5, "Checking-out vlog!"],
        [120.5, 123.0, "Bye!"],
    ],
    GH + "VID-20261108-WA0148.mp4": [[7.27, 10.4, "Guys, raat ke 1 baj rahe hai!"]],
    # ---- Juhu
    gx(JU, 10073): [
        [1.42, 3.42, "Hum finally beach pe aa chuke hai"],
        [3.42, 8.7, "Sabse interesting — hamara plan accidentally ban gaya beach aane ka"],
        [8.7, 13.4, "Aur main itni lucky hoon ki baaki sabne shoes pehne hai"],
        [13.42, 18.3, "I'm the only one who can enjoy the beach!"],
        [18.42, 20.3, "Aap sabhi ko kaisa lag raha hai?"],
        [20.36, 21.4, "Very good!"],
    ],
    gx(JU, 10085): [[0.56, 2.2, "Enjoy your chhoti kulfi, you know?"], [5.27, 5.9, "Enjoy!"]],
    gx(JU, 10115): [
        [0.21, 3.07, "Ye hai Juhu beach experience..."],
        [4.21, 5.33, "Ecstatic!"],
        [6.21, 8.11, "Juhu beach experience..."],
        [8.11, 10.15, "Okay... okay."],
    ],
    gx(GE, 10049): [[11.42, 15.0, "Sir, aapki max speed?"], [15.2, 17.2, "Meri? 2 kilometre per hour!"]],
    # ---- ETHGlobal
    gx(EG, 10204): [
        [0.66, 1.7, "Hi guys!"],
        [3.06, 6.56, "It's late night. Can you see the timing?"],
        [8.04, 11.88, "It's 3:12. I'm looking at my gadget"],
        [14.54, 17.94, "Many people are asleep, many people are awake"],
        [19.46, 24.66, "We are trying our best to be awake — our whole team"],
        [24.66, 27.5, "Abhinav, hi!"],
        [30.29, 31.89, "Yes, Soham"],
        [33.51, 40.0, "Hi Yash! You want to say hi to the camera?"],
        [47.13, 49.25, "Yash? Hi!"],
        [59.69, 61.73, "We have a lot to implement..."],
        [62.39, 65.65, "...so we are trying to be awake."],
    ],
    gx(EG, 10223): [
        [0.0, 2.0, "Late ho raha hai..."],
        [6.0, 8.0, "Samajh nahi aa raha"],
        [15.68, 17.68, "Ye aankhein toh laal ho gayi!"],
    ],
    gx(EG, 10234): [
        [1.71, 3.71, "Babu, uth ja!"],
        [3.71, 5.71, "Uth ja!"],
        [7.23, 8.43, "I'm going to sleep..."],
        [9.25, 10.99, "I'm going to sleep..."],
        [12.01, 13.23, "I'm going to sleep."],
    ],
    gx(EG, 10246): [[1.0, 3.76, "This is the dark chocolate from Kazakhstan"], [4.68, 6.3, "Let's open it!"]],
    # ---- Marine Drive
    MD + "VID-20261108-WA0141.mp4": [
        [9.0, 12.9, "Guys, so we are at Marine Drive, and this is it"],
        [12.9, 14.46, "So peaceful."],
        [14.46, 17.8, "So our hackathon ended today"],
    ],
    MD + "VID-20261108-WA0146.mp4": [
        [4.0, 7.0, "So guys, abhi ek bahut badi khushkhabri hai!"],
        [7.0, 10.0, "Hum Marine Drive aa chuke hai..."],
        [10.0, 12.0, "...and iske baad humein pata chala"],
        [12.0, 15.5, "ki hum Arkiv track mein jeet chuke hai!"],
        [18.04, 21.14, "It's a big deal — we won $1,000!"],
        [24.92, 25.6, "How are you feeling?"],
        [26.52, 27.96, "I am [beep] crazy, bro!"],
        [27.96, 32.54, "Didn't even know we'd get selected... literally crazy"],
        [32.54, 34.28, "We didn't have any idea!"],
        [38.7, 40.86, "Didi, how are you feeling?"],
        [41.3, 42.2, "Amazing!"],
        [44.76, 50.02, "He is so shocked he can't even speak"],
        [50.02, 52.52, "See his face once!"],
        [60.44, 63.58, "So, it was worth it — Mumbai trip!"],
    ],
    MD + "VID-20261108-WA0143.mp4": [
        [0.0, 1.1, "Hi!"],
        [10.0, 12.0, "Ye itni bakwaas chocolate hai..."],
        [12.0, 14.0, "Poochho mat, but mujhe itni meethi aur achhi lag rahi hai"],
        [14.0, 16.0, "Crazy ekdum!"],
        [16.0, 18.0, "Aur 150 ki — bilkul bhi achhi nahi thi"],
        [18.0, 22.86, "But mujhe bahut badhiya lagi, pata nahi kyun — kuch toh special hua aaj"],
        [48.94, 50.94, "Aaj hum camera bhool gaye..."],
        [50.94, 53.2, "...aur aaj sabse main din hai!"],
    ],
    MD + "VID-20261108-WA0149.mp4": [
        [15.22, 16.76, "So how are you feeling?"],
        [19.24, 26.68, "It's confirmed — we have won the second place in the Arkiv track"],
        [26.68, 28.32, "...and we have won $1,000!"],
        [29.38, 31.26, "How are you feeling as a team leader?"],
        [41.74, 45.42, "By the way, he has been a great team leader"],
        [45.86, 47.56, "And I got to learn a lot"],
        [48.44, 50.5, "Divija didi, how has your experience been?"],
        [50.66, 53.58, "One thing is confirmed — our group was very, very lucky"],
        [72.4, 78.2, "Jitne bhi humne khud se paise bhare the Mumbai aane ke..."],
        [78.2, 79.4, "...ab hum jeet chuke hai"],
        [80.9, 85.4, "Rehne ka, khaane ka, aane-jaane ka — jitna bhi kharcha hua"],
        [88.08, 92.22, "So you can say it's become a sponsored trip!"],
    ],
    gx(MD, 10321): [
        [7.22, 8.64, "Mumbai mein aakhri din..."],
        [8.64, 10.96, "And it was all great"],
        [11.54, 13.0, "All the good things happened"],
        [28.6, 30.04, "Good memories from Mumbai"],
        [30.04, 33.12, "They say Mumbai is a city of dreams"],
        [33.76, 36.28, "And it's true for us"],
        [36.28, 39.12, "Marine Drive — yes!"],
        [39.78, 41.5, "It's like a movie!"],
    ],
    # ---- Cat Café (from the Cat Café vlog's verified captions)
    gx(CC, 10274): [
        [0.75, 2.85, "Toh guys, basically abhi hum jaa rahe hai"],
        [2.85, 4.49, "cat cafe dekhne!"],
        [5.25, 7.87, "Kuch toh cool sa scenario hai wahan par"],
    ],
    gx(CC, 10275): [[40.88, 42.10, "He's very friendly"]],
    gx(CC, 10288): [
        [13.04, 15.0, "Kaisa laga cat cafe?"], [15.04, 17.0, "Bahut chill hai!"],
        [19.04, 21.0, "Kaisa laga cat cafe?"], [21.04, 23.0, "Bahut hi cute hai!"],
        [23.04, 25.0, "Aur ye billi dekho, kitni cute hai ye"],
    ],
    gx(CC, 10290): [
        [0.76, 2.58, "Bhai saab, ye kitni pyaari hai!"], [2.58, 4.52, "Look at this"],
        [4.52, 8.68, "She's the queen cat"], [8.68, 11.46, "Kitne aesthetic tarike se so rahi hai"],
    ],
    gx(CC, 10308): [
        [1.89, 4.31, "It's very casual, so it's rather comfortable over here"],
        [4.71, 6.17, "Sheena wants to sleep..."],
        [6.45, 8.53, "...and she wants me to keep petting her"],
        [9.65, 10.23, "You see?"],
    ],
    gx(CC, 10319): [[0.46, 2.2, "Bye bye!"]],
    # ---- Jio World
    JI + "VID-20261107-WA0002.mp4": [[0.02, 5.0, "Guys, ye hai Soham..."], [5.02, 8.0, "He is wearing the Meta glasses!"]],
    # ---- shayari (sleeper bus). Last words of both poems are uncertain: ask the poets.
    gx(SH, 10040): [
        [0.5, 2.86, "Oye ruko, wahi padhne taiyaar ho raha hai"],
        [2.86, 5.86, "Usse bhi read karne dena chahiye... par cheating ho rahi hai!"],
    ],
    gx(SH, 10041): [
        [1.07, 4.39, "Dua bhi tumhare liye, aur tumse hi ye gila"],
        [4.57, 8.91, "Agar hum tumhare, aur tum bhi tumhare — to phir humein kya mila?"],
        [9.27, 12.87, "Ye bechaini, ye kasak, aur dil lagaane ka ye sila"],
        [15.99, 22.6, "Ab to bas isi aas mein hai chala — ki kam se kam dosti ka rishta hi..."],
    ],
    gx(SH, 10038): [
        [20.83, 23.0, "Waah, waah, waah!"],
        [23.0, 27.99, "...jab meri pasandida aurat mujhe friend-zone karke chali gayi"],
        [27.99, 29.99, "Friend zone kya hota hai?"],
        [29.99, 31.6, "Friend zone!"],
    ],
    gx(SH, 10042): [
        [0.11, 6.57, "Tumhe kabhi poora likhun, ya kabhi adhoora likhun"],
        [6.57, 9.59, "Kabhi tumhe savera likhun, to kabhi chaand-sitaara likhun"],
        [9.59, 12.61, "Main likhun dilkashi, to tera muskurana likhun"],
        [12.61, 16.81, "Main likhun khwaab, to use tera husn likhun"],
        [16.81, 20.03, "Main likhun ishq, to use tera muskurana likhun"],
        [20.03, 22.95, "Main likhun tujhpe, to main tumhara aadaab likhun"],
        [22.95, 26.25, "Main likhun umeed, to main teri aankhein likhun"],
        [26.25, 29.35, "Main jab bhi likhun, mujhe tera likhun"],
        [29.35, 35.35, "Likh doon tere baare mein sab kuch, bas tujhe mera na likh sakun"],
        [35.35, 41.35, "Ek sawaal ye bhi hai — in chand kaagazon mein tujhe kaise likhun"],
        [41.35, 44.35, "Koi poochhe is rishte ka kya naam likhun..."],
        [44.35, 47.3, "...to main khud ko aankhein aur tujhe armaan likhun"],
    ],
}

# ---- full-scene pass (Nov 10): lines for the parts of clips that the first cut trimmed away.
# Words from large-v3 / turbo in Hindi mode, meaning checked against the English pass; unclear lines left out.
EXTRA = {
    TR + "GX010090.MP4": [
        [10.54, 14.0, "Pata hai, is wale bande ke upar na abhi chidiya ne beat kari..."],
        [14.0, 17.54, "...isko apni shirt badalni padi!"],
        [17.54, 20.54, "Aur hamare yahan aisa maana jaata hai ki ye bahut shubh hota hai"],
        [20.54, 24.04, "Haan — so let's see, ye shubh hota hai ki nahi hamare liye"],
        [24.04, 28.0, "Ho gaya waise sabka?"],
    ],
    TR + "GX010093.MP4": [
        [44.3, 47.8, "Toh ye hoga hamara introduction"],
        [47.8, 51.5, "Mumbai chalke dikhate hai aapko — kaisa raha hamara adventure"],
    ],
    gx(TR, 10027): [
        [0.0, 7.0, "Toh basically, teen buses hai — dekhte hai pehle Mumbai kaun pahunchti hai"],
        [7.0, 10.8, "Toh ye pehli bus hai..."],
        [10.8, 13.0, "...ye hai Hans..."],
        [13.0, 17.0, "...aur ye hamari. Dekhte hai kaun pehle pahunchti hai!"],
    ],
    TR + "VID-20261108-WA0147.mp4": [
        [30.34, 34.1, "Wo hamari taraf hi dekh raha tha — hamara welcome kar raha hai"],
        [34.1, 40.8, "Let's meet him soon... and this is the hotel where we get down"],
        [40.8, 44.5, "Let's have some food!"],
    ],
    GH + "VID-20261108-WA0098.mp4": [
        [29.55, 35.6, "Hamara room is better than both of theirs!"],
        [35.6, 39.4, "Enjoy tea in Mumbai!"],
        [39.5, 40.9, "Bye!"],
    ],
    gx(GE, 10049): [
        [1.3, 6.4, "Toh main pooch raha tha — aapki max speed bataiye"],
        [7.4, 10.4, "Abhi do kilometre chalna hai... dekhna hai ki nahi?"],
    ],
    gx(JU, 10103): [
        [0.0, 4.5, "Toh guys, hum aaye hai Juhu Beach..."],
        [4.5, 10.56, "...aur plan chal raha hai ki is launde ko sand mein ghusa ke mummy bana diya jaaye!"],
    ],
    gx(TR, 10256): [
        [3.9, 7.9, "We are going back to our guest house after two days"],
        [8.9, 10.9, "Last night was very difficult"],
        [11.9, 19.9, "And this is the iconic Nita Mukesh Ambani Cultural Centre"],
        [20.9, 22.9, "The lights at night, right?"],
    ],
    MD + "VID-20261108-WA0143.mp4": [
        [20.78, 23.4, "Kuch toh special hua hai aaj"],
        [54.5, 58.6, "This is the place, Marine Drive — our friends missed out on a lot today"],
        [63.0, 68.2, "This is the beach... Marine Drive"],
        [68.3, 71.9, "Ab Marine Drive ke saath ek special memory jud gayi"],
    ],
    MD + "VID-20261108-WA0146.mp4": [
        [0.0, 3.6, "Results bhi aa gaye? Perfect — ye dekho, result!"],
    ],
    MD + "VID-20261108-WA0149.mp4": [
        [0.0, 6.6, "Guys, so now we're at Marine Drive — a popular food plaza with lots of stalls"],
        [7.8, 10.5, "So we've ordered something here"],
        [54.0, 58.0, "Starting with the beat — that was actually lucky!"],
        [58.0, 60.8, "Abhinav abhi mummy se baat karne gaya"],
        [60.8, 62.6, "Maine apni mummy se baat kar li"],
        [62.6, 64.4, "...and they were very happy"],
        [66.1, 70.6, "Isse bhi zyada khushiyaan..."],
    ],
    GH + "VID-20261108-WA0148.mp4": [
        [2.27, 4.27, "Kitna time hoga?"],
        [10.4, 12.27, "...aur bhookh lag rahi hai"],
        [12.27, 16.27, "Basically hamein bhookh lagi thi, toh humne khaana mangwaya"],
        [22.27, 31.5, "Isne waffles — pancakes mangwaye the. Bolta hai, taste karna, kitna crazy hota hai"],
        [31.5, 39.5, "Humne poocha ye packed kyun aaya — bolta hai, ye tumhe grocery store pe nahi milega"],
        [40.5, 43.9, "Toh phir isne khola — aur andar se kya nikla?"],
        [46.7, 50.1, "Ye aata hai!"],
        [57.0, 61.5, "Iske 200 rupaye liye... nahi, 100 rupaye"],
    ],
    gx(GH, 10273): [
        [10.56, 13.56, "So this is our corridor"],
        [13.56, 20.6, "Ye ladkon ka room tha"],
        [20.7, 22.3, "This is my room"],
        [29.3, 32.0, "This was our room"],
        [32.22, 37.73, "It was so pretty — in ladkon ke room se toh zyada achha tha"],
        [37.73, 40.73, "It has windows on three sides"],
        [40.73, 43.73, "And also, hamara kaanch ka bana tha"],
        [44.0, 46.4, "So much better — and the view is good"],
        [73.2, 77.4, "And our bathroom was also bigger"],
        [77.7, 79.1, "By the way, this is a sheesha"],
        [82.7, 84.4, "Aaj Diwali hai — happy Diwali!"],
        [88.0, 90.3, "This is another sheesha"],
        [91.6, 95.3, "And this is the bathroom — jo kaafi bada tha"],
        [98.0, 100.4, "Like, kaafi spacious"],
    ],
    gx(EG, 10204): [
        [54.33, 57.73, "Can we see — sab kitne soye-soye se lag rahe hai?"],
    ],
    gx(JI, 10222): [
        [21.9, 26.0, "Largest passenger elevator in the world!"],
        [167.0, 174.5, "Even in the washrooms, all the decorations had real flowers"],
        [176.0, 182.0, "You can see the intricate details"],
    ],
    gx(MD, 10321): [
        [16.0, 18.0, "Any comments?"],
        [20.0, 22.0, "Five-star experience!"],
        [22.0, 24.0, "Out of?"],
        [24.0, 26.0, "Five-star!"],
    ],
    gx(SH, 10040): [
        [5.86, 13.0, "Ye kya hai — jab main unse umeed chhodne ke baad phir se unhi ke khayal mein padta hoon"],
        [13.0, 15.34, "Arre yaar, wo tu chhod na — tu neeche dekh"],
        [15.34, 20.18, "Ek baar read maan le, toh uske baad shuru kare"],
    ],
    JI + "VID-20261107-WA0001.mp4": [
        [0.0, 8.16, "Toh guys, ghoomte-phirte abhi hum Nita Mukesh Ambani Cultural Centre mein hai"],
        [12.84, 15.66, "Aisa lag raha hai hum doosri hi duniya mein aa gaye hai"],
        [50.78, 55.2, "You have superpowers now — yay!"],
    ],
    JI + "VID-20261107-WA0002.mp4": [
        [8.0, 15.6, "Wow, I mean it has an AI assistant — try talking to it"],
        [15.6, 24.5, "What is it saying? Okay, try giving some instructions"],
        [24.5, 38.3, "Does it respond? Wow!"],
        [38.34, 40.34, "Can you hear it in your ears?"],
        [40.34, 42.34, "Yeah! — Wow, I cannot hear it"],
        [42.34, 46.34, "So guys, we are trying out Meta glasses"],
        [46.34, 55.34, "Finally — the first person in his whole family to wear it"],
        [56.34, 58.34, "Let's try wearing it"],
        [59.34, 61.34, "Is it okay? — Thank you"],
        [67.05, 69.05, "So this is how I look"],
        [69.05, 80.77, "Hi Meta, what are you seeing right now?"],
        [80.77, 87.12, "Are you seeing something?"],
        [87.12, 89.0, "Bye guys!"],
    ],
}
for _k, _v in EXTRA.items():
    CAP[_k] = sorted(CAP.get(_k, []) + _v)
