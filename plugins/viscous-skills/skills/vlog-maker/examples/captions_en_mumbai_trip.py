"""English captions for the Mumbai trip (Nov 11: captions in English everywhere except the shayari).

EN maps each Hinglish line in captions.CAP to its English meaning; lines that are already English are not
listed and pass through unchanged. build_trip.clip() applies it to every clip outside the shayari/ folder.
"""

EN = {
    # departure
    "Hey guys, toh hum jaa rahe hai ETH Hackathon pe": "Hey guys, so we're off to the ETH Hackathon",
    "Abhi hum hackathon ke liye nikle hai — cab se, bus ke liye": "We've just left for the hackathon — by cab, to catch the bus",
    "Toh chalo, sab introduction dete hai": "So come on, everyone introduce yourselves",
    "Pehle main Yash, aur ye meri team hai!": "First up, I'm Yash, and this is my team!",
    "Hi bolo guys!": "Say hi, guys!",
    "Ek ek karke introduction": "Introductions, one by one",
    "Hello guys, mera naam hai Abhinav": "Hello guys, my name is Abhinav",
    "Hum log ab chale bus stand ke liye — wahan Divija di humara wait kar rahi hai":
        "We're heading to the bus stand now — Divija di is waiting for us there",
    "So guys, abhi hum bus stop pe wait kar rahe hai": "So guys, right now we're waiting at the bus stop",
    "Pata hai, is wale bande ke upar na abhi chidiya ne beat kari...": "You know, a bird just pooped on this guy...",
    "...isko apni shirt badalni padi!": "...he had to change his shirt!",
    "Aur hamare yahan aisa maana jaata hai ki ye bahut shubh hota hai": "And where we come from, that's considered really lucky",
    "Haan — so let's see, ye shubh hota hai ki nahi hamare liye": "Yeah — so let's see if it turns out lucky for us",
    "Ho gaya waise sabka?": "Is everyone done, by the way?",
    "Toh guys, Mumbai gang ready ho chuki hai, aur bus bhi nikal chuki hai":
        "So guys, the Mumbai gang is ready, and the bus has left too",
    "Toh ye hoga hamara introduction": "So that was our introduction",
    "Mumbai chalke dikhate hai aapko — kaisa raha hamara adventure": "Come along to Mumbai — we'll show you how our adventure went",
    # expressway / arrival
    "Toh basically, teen buses hai — dekhte hai pehle Mumbai kaun pahunchti hai":
        "So basically, there are three buses — let's see which one reaches Mumbai first",
    "Toh ye pehli bus hai...": "So this is the first bus...",
    "...ye hai Hans...": "...this is Hans...",
    "...aur ye hamari. Dekhte hai kaun pehle pahunchti hai!": "...and this is ours. Let's see who gets there first!",
    "Wo hamari taraf hi dekh raha tha — hamara welcome kar raha hai": "He was looking right at us — welcoming us",
    # hotel
    "Toh ye hamara guest house ka room hai, Abhinav bhai": "So this is our room, Abhinav bhai",
    "So guys, we are ready — abhi hum hackathon ke liye jaane wale hai": "So guys, we are ready — we're about to leave for the hackathon",
    "Co-founder saab, are you ready?": "Co-founder sir, are you ready?",
    "Bilkul!": "Absolutely!",
    "[beep] faadni hai!": "We're gonna kick some [beep]!",
    "Sab log bahut excited hai": "Everyone is super excited",
    "Let's see, hackathon mein kuch toh hoga...": "Let's see, something's going to happen at the hackathon...",
    "Hamara room is better than both of theirs!": "Our room is better than both of theirs!",
    "Ye ladkon ka room tha": "This was the boys' room",
    "It was so pretty — in ladkon ke room se toh zyada achha tha": "It was so pretty — way better than the boys' room",
    "And also, hamara kaanch ka bana tha": "And also, ours was made of glass",
    "Raat ko lights bahut achhi lagti hai": "The lights look really nice at night",
    "Aaj Diwali hai — happy Diwali!": "It's Diwali today — happy Diwali!",
    "And this is the bathroom — jo kaafi bada tha": "And this is the bathroom — which was pretty big",
    "Like, kaafi spacious": "Like, really spacious",
    "Kitna time hoga?": "What time is it?",
    "Guys, raat ke 1 baj rahe hai!": "Guys, it's 1 AM!",
    "...aur bhookh lag rahi hai": "...and we're hungry",
    "Basically hamein bhookh lagi thi, toh humne khaana mangwaya": "Basically we were hungry, so we ordered food",
    "Isne waffles — pancakes mangwaye the. Bolta hai, taste karna, kitna crazy hota hai":
        "He ordered waffles — pancakes. He says, taste it, it's crazy",
    "Humne poocha ye packed kyun aaya — bolta hai, ye tumhe grocery store pe nahi milega":
        "We asked why it came packed — he says, you won't find this at a grocery store",
    "Toh phir isne khola — aur andar se kya nikla?": "So then he opened it — and what came out?",
    "Ye aata hai!": "This is what you get!",
    "Iske 200 rupaye liye... nahi, 100 rupaye": "They charged 200 rupees for this... no, 100 rupees",
    # Juhu
    "Hum finally beach pe aa chuke hai": "We've finally made it to the beach",
    "Sabse interesting — hamara plan accidentally ban gaya beach aane ka":
        "Most interesting part — our beach plan happened by accident",
    "Aur main itni lucky hoon ki baaki sabne shoes pehne hai": "And I'm so lucky that everyone else is wearing shoes",
    "Aap sabhi ko kaisa lag raha hai?": "How's everyone feeling?",
    "Enjoy your chhoti kulfi, you know?": "Enjoy your little kulfi, you know?",
    "Ye hai Juhu beach experience...": "This is the Juhu Beach experience...",
    "Juhu beach experience...": "Juhu Beach experience...",
    "Toh main pooch raha tha — aapki max speed bataiye": "So I was asking — tell us your max speed",
    "Abhi do kilometre chalna hai... dekhna hai ki nahi?": "We still have to walk two kilometres... shall we see?",
    "Sir, aapki max speed?": "Sir, your max speed?",
    "Meri? 2 kilometre per hour!": "Mine? 2 kilometres per hour!",
    "Toh guys, hum aaye hai Juhu Beach...": "So guys, we've come to Juhu Beach...",
    "...aur plan chal raha hai ki is launde ko sand mein ghusa ke mummy bana diya jaaye!":
        "...and the plan is to bury this guy in the sand and turn him into a mummy!",
    # ETHGlobal night
    "Can we see — sab kitne soye-soye se lag rahe hai?": "Can we see — how sleepy everyone looks?",
    "Late ho raha hai...": "It's getting late...",
    "Samajh nahi aa raha": "Can't figure it out",
    "Ye aankhein toh laal ho gayi!": "These eyes have gone red!",
    "Babu, uth ja!": "Babu, wake up!",
    "Uth ja!": "Wake up!",
    # Jio World Centre
    "Guys, ye hai Soham...": "Guys, this is Soham...",
    "Toh guys, ghoomte-phirte abhi hum Nita Mukesh Ambani Cultural Centre mein hai":
        "So guys, wandering around, we're now at the Nita Mukesh Ambani Cultural Centre",
    "Aisa lag raha hai hum doosri hi duniya mein aa gaye hai": "It feels like we've walked into a whole other world",
    # Marine Drive
    "Results bhi aa gaye? Perfect — ye dekho, result!": "Results are out too? Perfect — look, the result!",
    "So guys, abhi ek bahut badi khushkhabri hai!": "So guys, we have some really big news!",
    "Hum Marine Drive aa chuke hai...": "We've come to Marine Drive...",
    "...and iske baad humein pata chala": "...and after that we found out",
    "ki hum Arkiv track mein jeet chuke hai!": "that we've won the Arkiv track!",
    "Ye itni bakwaas chocolate hai...": "This chocolate is so bad...",
    "Poochho mat, but mujhe itni meethi aur achhi lag rahi hai": "Don't ask, but it tastes so sweet and good to me",
    "Crazy ekdum!": "Totally crazy!",
    "Aur 150 ki — bilkul bhi achhi nahi thi": "And it cost 150 — it wasn't good at all",
    "But mujhe bahut badhiya lagi, pata nahi kyun — kuch toh special hua aaj":
        "But I loved it, don't know why — something special happened today",
    "Kuch toh special hua hai aaj": "Something special happened today",
    "Aaj hum camera bhool gaye...": "We forgot the camera today...",
    "...aur aaj sabse main din hai!": "...and today is the most important day!",
    "Ab Marine Drive ke saath ek special memory jud gayi": "Now Marine Drive holds a special memory for us",
    "Abhinav abhi mummy se baat karne gaya": "Abhinav just went to talk to his mom",
    "Maine apni mummy se baat kar li": "I've talked to my mom",
    "Isse bhi zyada khushiyaan...": "Even more happiness...",
    "Jitne bhi humne khud se paise bhare the Mumbai aane ke...": "All the money we paid ourselves to come to Mumbai...",
    "...ab hum jeet chuke hai": "...now we've won",
    "Rehne ka, khaane ka, aane-jaane ka — jitna bhi kharcha hua": "Stay, food, travel — whatever we spent",
    # last day / Cat Café
    "Mumbai mein aakhri din...": "Last day in Mumbai...",
    "Toh guys, basically abhi hum jaa rahe hai": "So guys, basically we're going now",
    "cat cafe dekhne!": "to check out a cat café!",
    "Kuch toh cool sa scenario hai wahan par": "There's something cool going on there",
    "Kaisa laga cat cafe?": "How was the cat café?",
    "Bahut chill hai!": "Super chill!",
    "Bahut hi cute hai!": "So cute!",
    "Aur ye billi dekho, kitni cute hai ye": "And look at this cat, she's so cute",
    "Bhai saab, ye kitni pyaari hai!": "Bro, she's so adorable!",
    "Kitne aesthetic tarike se so rahi hai": "Look how aesthetically she's sleeping",
}

# on-screen pops, labels and title cards (Nov 11: English too); names and English titles are not listed
TITLE_EN = {
    "...tabhi Divija ka phone aaya": "...then Divija got a call",
    "4 din pehle...": "4 days earlier...",
    "Ab Div ki baari": "Div's turn",
    "Bus mein shayari session": "Shayari session on the bus",
    "Chidiya ne beat kar di!": "A bird pooped on him!",
    "Devcon badge banao!": "Making Devcon badges!",
    "Ek phone call...": "One phone call...",
    "Full cat café vlog channel pe!": "Full cat café vlog on the channel!",
    "Hackathon khatam. Marine Drive.": "Hackathon over. Marine Drive.",
    "Hacking shuru!": "Hacking begins!",
    "Hamara Mumbai ghar": "Our Mumbai home",
    "Hamara hotel": "Our hotel",
    "Hamara Hotel": "Our Hotel",
    "Mumbai pahunch gaye!": "Made it to Mumbai!",
    "RESULT AA GAYA!": "THE RESULT IS IN!",
    "Raat ke 3 baje...": "3 AM...",
    "Shubh sanket?!": "A good omen?!",
    "7 NOV · RAAT": "7 NOV · NIGHT",
    "BLR → MUM · 5 DIN · 5 DOST": "BLR → MUM · 5 DAYS · 5 FRIENDS",
}
