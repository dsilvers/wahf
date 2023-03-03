# WAHoF

## Page Types

### Home Page

- Menus/navigation linking to other content
- Featured items that could highlight recent content
- Latest blog post(s)
- Recent inductee(s)
- Join/Donation drive
- Induction Ceremony event


### Magazine Viewer - List of Issues

- Publically viewable grid of magazine covers, maybe a blurb about the content inside.
- If they aren’t logged in, display a blurb about “join to view the magazine”


### Magazine Viewer - View Issue

- Only viewable by logged in members
- Non-members get redirected to an login/join page
- Display individual pages in the browser OR just let them download a PDF copy? (PDF is much less effort…)


### Blog Post List

- Chronologically sorted list of blog posts
- Could group/filter by tags if that seems appropriate


### Blog Post

- Contains “blocks” of content types that we get to design and define.
- These blocks contain text, images, video, or other content.
- Posts can contain multiple blocks of any number of types of content.
- For example, a big “hero” image on the top of the post, followed by a headline, a blurb of some text, several small images with captions, and maybe more text. It’s all pretty flexible.


### Inductee List

- Each inductee could have a photo assigned, you could automatically generate a fancy list of inductees with names/photos/dates however we see fit.


### Inductee Profile

- Could follow a similar style as the blog post “blocks” format, but add fields for dates, their name, or a profile photo.
- Can be as structured or flexible as we want it to be.


### Induction Ceremony

- Event Info
- Payment form


### Join

- Payment form for initial membership or renewal


### Generic Content Pages

This is freeform content wrapped in the website template. Essentially it’s an easy way to build out a page that doesn’t have structured content. You get a text box where you can format text and add images, to do whatever you need to do.  More flexible and less structured than a blog post.

Content that falls under this category could include:

- About Us
- Donate (embedded Stripe donation form, or links to paypal, write us a check, or whatever you think)
- Nominating an inductee instructions
- Aviation Scholarship Information
- Include past scholars?
- Contact Us

### Account Functions

These all are “batteries included” with Wagtail/Django. It mostly involves us applying design/styles and letting the magic do the rest, there’s not a lot we have to actually build out here.

- Password Reset
- Login
- Logout
- Admin Tools
