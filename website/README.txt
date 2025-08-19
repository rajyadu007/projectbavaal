cd website/


#Only first time
npm init -y


# to build new style.css
npm run watch:tailwind


python manage.py populate_influencer influencer_data.yaml

Update an existing influencer by slug (recommended)
python manage.py fetch_influencer_data --slug pooja-janrao --ig "@pooja_janrao_official" --yt https://www.youtube.com/@OfficialPoojajanrao --tw "@PoojaJanrao"

Create (or update) by name, and fetch
python manage.py fetch_influencer_data --name "Pooja Janrao" --ig "@pooja_janrao_official" --yt https://www.youtube.com/@SomeChannel --tw @SomeTwitter


Control how much content you pull
python manage.py fetch_influencer_data --slug pooja-janrao --max-ig-posts 8 --max-yt-videos 10 --max-tweets 5


python manage.py populate_influencer "Jane Smith" \
    --youtube-urls "https://www.youtube.com/watch?v=video1" "https://www.youtube.com/watch?v=video2" \
    --instagram-urls "https://www.instagram.com/p/image1/" "https://www.instagram.com/p/image2/" "https://www.instagram.com/p/image3/" \
    --tweet-urls "https://twitter.com/user/status/tweet1"