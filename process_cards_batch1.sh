#!/bin/bash

MATON_API_KEY="$MATON_API_KEY"
BASE_URL="https://gateway.maton.ai/trello/1"
READY_LIST="699f376e916d1293ac8a24c2"

# Function to add comment
add_comment() {
    local card_id="$1"
    local message="$2"
    curl -s -X POST \
        "${BASE_URL}/cards/${card_id}/actions/comments" \
        -H "Authorization: Bearer ${MATON_API_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"text\":\"${message}\"}"
}

# Function to move card
move_card() {
    local card_id="$1"
    curl -s -X PUT \
        "${BASE_URL}/cards/${card_id}" \
        -H "Authorization: Bearer ${MATON_API_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"idList\":\"${READY_LIST}\"}"
}

echo "Processing card 1: Kwalee - David Darling CBE"
MSG1="**DRAFTED OUTREACH MESSAGE:**\\n\\nSubject: Scaling Kwalee's live ops efficiently\\n\\nHi David,\\n\\nWith 500M+ downloads and hits like Draw It and Teacher Simulator, Kwalee has clearly mastered the hyper-casual playbook. Keeping that volume of titles fresh with live content is no small challenge.\\n\\nWe help top mobile publishers automate their live ops workflows—so your teams can ship more content updates without scaling headcount linearly. Our platform handles the production pipeline from concept to deployment, with analytics hooks built in.\\n\\nWould you be open to a brief 15-minute call to explore if this could help Kwalee scale even faster?\\n\\nBest,\\nLucas"
add_comment "69a8913a58bb8b5430028f6f" "$MSG1"
move_card "69a8913a58bb8b5430028f6f"
echo "✓ Card 1 complete"

echo ""
echo "Processing card 2: Supercent - Gong Jun-sik"
MSG2="**DRAFTED OUTREACH MESSAGE:**\\n\\nSubject: Congratulating Supercent on the Ministerial Award\\n\\nHi Gong,\\n\\nCongratulations on Supercent winning the 2024 Korea Content Awards Ministerial Award. Building a hit Kingdom series while maintaining publishing excellence at 111% is impressive.\\n\\nWe help hyper-casual publishers streamline their live ops and content production—enabling faster iteration cycles without expanding team size. Our automation platform has helped similar studios double their content output.\\n\\nWould you be open to a brief call to see how this might support Supercent's continued growth?\\n\\nBest,\\nLucas"
add_comment "69a7fc7e065b150b2ebfef26" "$MSG2"
move_card "69a7fc7e065b150b2ebfef26"
echo "✓ Card 2 complete"

echo ""
echo "Processing card 3: Moonee - Erez Mishli"
MSG3="**DRAFTED OUTREACH MESSAGE:**\\n\\nSubject: Live ops scaling for Moonee\\n\\nHi Erez,\\n\\nMoonee's focus on monetization optimization for mobile games shows you understand what drives sustainable revenue in today's market.\\n\\nWe help mobile publishers automate their live ops infrastructure—delivering personalized content at scale while reducing operational overhead. This means better monetization without burning out your team.\\n\\nWould you be open to a brief 15-minute call to explore if this aligns with Moonee's roadmap?\\n\\nBest,\\nLucas"
add_comment "69a8913bac68accb5d3998a0" "$MSG3"
move_card "69a8913bac68accb5d3998a0"
echo "✓ Card 3 complete"

echo ""
echo "Processing card 4: TapNation - Hervé Montoute"
MSG4="**DRAFTED OUTREACH MESSAGE:**\\n\\nSubject: Congrats on 1B downloads + scaling live ops\\n\\nHi Hervé,\\n\\nHitting 1 billion downloads and acquiring UAhero shows TapNation is playing at the top of the hyper-casual game. That's serious scale.\\n\\nWe help publishers at your level automate their live ops workflows—so you can keep pumping out hits like Ice Cream Inc without the content production becoming a bottleneck.\\n\\nWould you be open to a brief call to see how we could help TapNation maintain this momentum?\\n\\nBest,\\nLucas"
add_comment "69a8913bf097d06ca2980bab" "$MSG4"
move_card "69a8913bf097d06ca2980bab"
echo "✓ Card 4 complete"

echo ""
echo "Processing card 5: Devsisters - Gil-Hyun Cho"
MSG5="**DRAFTED OUTREACH MESSAGE:**\\n\\nSubject: Cookie Run's expansion to Roblox + live ops\\n\\nHi Gil-Hyun,\\n\\nExpanding Cookie Run to Roblox in 2026 is a bold move that shows Devsisters knows how to evolve with the market. Managing multiple platforms while keeping the core experience fresh is a significant operational challenge.\\n\\nWe help midcore studios automate their live ops across platforms—ensuring consistent content delivery whether players are on mobile or metaverse. This lets your team focus on creative rather than logistics.\\n\\nWould you be open to a brief call to explore how this could support the Roblox expansion?\\n\\nBest,\\nLucas"
add_comment "69a7fcc1bf5a87c56d8d9f88" "$MSG5"
move_card "69a7fcc1bf5a87c56d8d9f88"
echo "✓ Card 5 complete"

echo ""
echo "Processing card 6: Playgendary - Dmitriy Shelengovskiy"
MSG6="**DRAFTED OUTREACH MESSAGE:**\\n\\nSubject: Live ops at 2B+ installs scale\\n\\nHi Dmitriy,\\n\\nWith 2B+ installs and 300+ employees across multiple offices, Playgendary has built something serious. Managing live ops for hits like Kick the Buddy and Tank Stars at that scale is no joke.\\n\\nWe help large mobile studios automate their content production pipelines—so distributed teams can ship coordinated updates without chaos. Our platform keeps everyone aligned from concept to deployment.\\n\\nWould you be open to a brief 15-minute call to see if this could streamline operations at Playgendary?\\n\\nBest,\\nLucas"
add_comment "69a891e65140c682359d95d8" "$MSG6"
move_card "69a891e65140c682359d95d8"
echo "✓ Card 6 complete"

echo ""
echo "Processing card 7: Azur Games - Dmitry Yaminsky"
MSG7="**DRAFTED OUTREACH MESSAGE:**\\n\\nSubject: 8B installs - scaling live ops at Azur\\n\\nHi Dmitry,\\n\\nTopping 8 billion installs puts Azur Games in rare company. Maintaining live content across that volume of titles requires serious operational muscle.\\n\\nWe help hyper-casual leaders automate their live ops workflows—so you can keep that rapid test-and-learn cycle going without the content production becoming a constraint.\\n\\nWould you be open to a brief call to explore how this could help Azur scale even further?\\n\\nBest,\\nLucas"
add_comment "69a956ec032c008646fd260a" "$MSG7"
move_card "69a956ec032c008646fd260a"
echo "✓ Card 7 complete"

echo ""
echo "Processing card 8: Lion Studios (AppLovin) - Rafael Vivas"
MSG8="**DRAFTED OUTREACH MESSAGE:**\\n\\nSubject: Live ops for AppLovin's publishing arm\\n\\nHi Rafael,\\n\\nLeading Lion Studios means managing live ops across one of the industry's largest publishing portfolios. With AppLovin's backing, the scale is massive.\\n\\nWe help large publishers automate their live ops infrastructure—enabling consistent content delivery across dozens of titles without proportional headcount growth.\\n\\nWould you be open to a brief 15-minute call to see if this could optimize Lion Studios' operations?\\n\\nBest,\\nLucas"
add_comment "69a956f46890fd5af868396d" "$MSG8"
move_card "69a956f46890fd5af868396d"
echo "✓ Card 8 complete"

echo ""
echo "Processing card 9: BoomBit - Marcin Olejarz"
MSG9="**DRAFTED OUTREACH MESSAGE:**\\n\\nSubject: Analytics for publicly-traded gaming\\n\\nHi Marcin,\\n\\nAs a publicly-traded company with 1.7B+ downloads, BoomBit faces the dual challenge of driving product excellence while maintaining investor-grade reporting transparency.\\n\\nWe help public gaming companies automate their analytics infrastructure—delivering real-time portfolio dashboards and automated investor reporting that keeps leadership and shareholders aligned.\\n\\nWould you be open to a brief call to explore how this could support BoomBit's public market obligations?\\n\\nBest,\\nLucas"
add_comment "69a8913a84d065cf67ed64e6" "$MSG9"
move_card "69a8913a84d065cf67ed64e6"
echo "✓ Card 9 complete"

echo ""
echo "Processing card 10: PlaySimple - Yoav Ecker"
MSG10="**DRAFTED OUTREACH MESSAGE:**\\n\\nSubject: Daily content automation for word games\\n\\nHi Yoav,\\n\\nPlaySimple's daily engagement model with Word Trip and Daily Themed Crossword requires relentless content production. As part of MTG's Casual District, that operational excellence is now backed by serious resources.\\n\\nWe help word game studios automate their daily content pipelines—enabling faster puzzle generation, personalization at scale, and streamlined live ops that keep players coming back every day.\\n\\nWould you be open to a brief 15-minute call to see how this could optimize PlaySimple's content operations?\\n\\nBest,\\nLucas"
add_comment "69a7fcc0964a8fa7e29a1d86" "$MSG10"
move_card "69a7fcc0964a8fa7e29a1d86"
echo "✓ Card 10 complete"

echo ""
echo "=========================================="
echo "COMPLETED: 10 cards processed"
echo "=========================================="
