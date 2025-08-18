cd website/


#Only first time
npm init -y


# to build new style.css
npm run watch:tailwind

Update an existing influencer by slug (recommended)
python manage.py fetch_influencer_data --slug pooja-janrao --ig "@pooja_janrao_official" --yt https://www.youtube.com/@OfficialPoojajanrao --tw "@PoojaJanrao"

Create (or update) by name, and fetch
python manage.py fetch_influencer_data --name "Pooja Janrao" --ig "@pooja_janrao_official" --yt https://www.youtube.com/@SomeChannel --tw @SomeTwitter


Control how much content you pull
python manage.py fetch_influencer_data --slug pooja-janrao --max-ig-posts 8 --max-yt-videos 10 --max-tweets 5
