# How an Agent Finds Creators on Xiaohongshu: Tested Process

> This process has been field-tested. It works for any region and any topic.

## Step 1: Log in by scanning the QR code

- Open **www.xiaohongshu.com** in the agent's browser.
- The account owner scans the QR code with the Xiaohongshu app. The agent never types a username or password.
- Run all searches and profile views on the **xiaohongshu.com** domain. Without a login, an overseas IP may be redirected to the international site rednote.com, but the login session only works on xiaohongshu.com.
- **Search does not work without a login**: the site shows a "Log in to view search results" pop-up.

## Step 2: Search by keyword

- Build keywords as **region + audience + life scenario**, e.g. "<city> + study-abroad daily life", "<country> + life sharing", "<school> + daily", "<country> + Chinese daily life". Add a specific scene for more small creators, e.g. 悉尼 + 早八 (Sydney + 8am class), 墨尔本 + 租房日常 (Melbourne + renting life).
- Use lifestyle words only. Do not search insurance or doctor words: we want lifestyle creators, and the insurance topic goes into the collaboration brief.
- Keep keywords broad. Narrow ones (product names, industry terms) mostly surface institutional or agency accounts, or match unrelated meanings of the same word.
- Each keyword shows about 20 notes on the first screen, with title, author, post time and like count.
- The default "comprehensive" sort shows big accounts and viral posts first. **To find small creators**, open notes posted minutes to hours ago with single- or double-digit likes, then go to the author's profile.

**Snowball from a good creator.** When a creator fits, look at the similar accounts the
platform suggests on their profile and at the people active in their comments, and open the
ones that look like small lifestyle creators. Browse by hand, one at a time. Do not use
third-party extensions that bulk-export "similar creators" or bulk-email them: they break
the platform's user agreement, risk the account, and send creator data to a third party.

## Step 3: Review the profile

| Field | Where | Notes |
|---|---|---|
| Followers / Following / Likes & Collects | Top of profile | Tiers: <500 / 500–1k / 1k–2k / 2k+ |
| Xiaohongshu ID (小红书号) and User ID | Under the nickname; User ID is in the profile URL | Record both |
| IP Location (IP属地) | Next to the Xiaohongshu ID | Visible on most accounts. If it is missing on the profile, open a note: the date line and the comments show the IP |
| Bio | Under the nickname | Shows identity (school, city, years living locally) and commercial signals (business email, "DM for collaboration", verified creator tags) |
| Notes list | Lower part of profile | **No dates on the profile**. Estimate frequency from the number of notes, or open the latest note to see its date |
| Replies to comments | Inside a note | Look for replies tagged "Author". This takes time, so spot-check only 1–2 notes |

## Step 4: Decide if the creator is a fit

**Fit (prioritise):**
- IP location matches the target region, and the bio or content confirms identity (current student, or a long-term local resident)
- Followers within the target band (e.g. <2k), posted in the last 1–2 weeks
- Real everyday-life content (cooking, classes, part-time work, renting, weekends) in their own voice
- Active comments with replies from the author

**Exclude or downgrade:**
- Institutional, student-union, agency, clinic or merchant accounts
- Accounts promoting competitors, or mainly selling their own services
- **Suspected matrix/marketing accounts**: newly created, following count in single digits; likes tens of times higher than followers; every title is "flag emoji + question" bait; frequent soft restaurant ads; IP location hidden
- Suspected fake followers: thousands of followers but only 10–20 likes per post; or following far more accounts than follow them (follow-for-follow)
- Above the target follower band (keep 2k+ as reference only)

## Step 5: Record

Record each creator in the Creator Library with these fields:

> Library ID | Platform | Category | Nickname | Xiaohongshu ID | User ID | Profile URL | Followers + Tier | Likes & Collects | Following | IP Location | City | Identity | Content Focus | Source Keyword | Ad / Collab Signals | Red Flags | Score | Status

Take screenshots at the key steps: search results, a profile (showing followers and IP location), and comments (showing IP and author replies).

## Next step: open a 蒲公英 account (recommended)

This process finds and screens creators from their public profiles. Before paying anyone,
Medibank should open a **蒲公英 (Pugongying) brand account**, Xiaohongshu's official creator
marketplace:

- **See the creator's back-end data**, not only the public profile: audience profile
  (location, age, gender), reach and engagement on past notes, and quoted price. This is the
  data a profile scan cannot show, and it feeds the full score in `tools/kol_score.py`.
- **It is the only allowed route for paid collaborations.** Paid notes go through 蒲公英 and
  carry the sponsor tag; private deals are penalised by the platform
  (`references/platforms/xiaohongshu.md`).
- **MCN agencies** manage groups of creators and can book several at once, but the booking
  still goes through 蒲公英 with the tag. Check that the agency's creators pass the same
  screening.
- Very small creators may be below 蒲公英's entry threshold
  (`references/kol-playbook.md` §1). Any gifted or paid post from them must still be
  labelled as an ad.

So: use this process to build the shortlist, then look up each shortlisted creator in
蒲公英 for the back-end data and book there. [VERIFY current 蒲公英 data fields and entry
rules with Xiaohongshu]

## Operating rules

- Browse at a human pace: wait 3–5 seconds between actions and open only 3–5 profiles per keyword.
- View only: **no likes, follows, comments or DMs**, and no bulk scraping.
- The searches run on the account owner's real account. Profiles may show relationships such as "mutual follow", and browsing may change that account's feed recommendations.
- At this pace, about 40 page views in testing triggered no captcha or rate limit.
