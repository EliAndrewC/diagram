# Feature 389 - the GM's request, verbatim

Dictated; the session's reading of dictation errors is noted in [brackets] only where a word would otherwise mislead.

## 2026-10-18, first message

> I would like to develop a money skill that has to do with actually having a coherent way of figuring out what stuff costs based largely on historical research, both that we have already done and that I will have you do. With regards to the historical research, the diagram repository already has a well-established system for this, and I wonder if we would be able to essentially make use of their system without just having to re-implement it. Um, I mean, I guess we could just like copy their subagent definitions into this project, and we might need to modify them anyway, so that's maybe like a good idea. I don't know. What do you think about that? Because I do think that like doing research Uh, in order to be rigorous, we are going to want to basically do what they are doing anyway, so therefore I expect that we will need to have our own, like, subagent stuff, uh, or somehow just, like, directly import a lot of what they're doing. What do you think?

## 2026-10-18, second message (excerpt)

> I mean, we will definitely want to do our own independent research as part of this, though it sounds like you're saying that I would do that research in the diagram repo, if I understand you correctly. Is that what you're saying? and then you would pull from their research findings in order to make the money skill?
>
> If we do it that way, then probably what I would end up doing in these cases when I'm having you work is I would start a diagram session and then you and that session could use GitHub issues to coordinate. [...] then basically you would say what research you need, they would do the research, and then you would be able to pull the research when they're done. Is that right?
>
> I can also share with you a lot of notes that we have over the years. I have created a new money folder in the main L7R checkout on the host. [...] Basically, uh, the basis of the work that we have done so far involves the concept of purchasing power parity, in which we take a basket of goods from Amazon and then, you know, figure out how much 40 gallons of rice, which is essentially what a koku is, uh, actually costs, and then converting that to US dollars [...] the answer was that a koku was about $550, although uh, with inflation, I'm sure that the number is different now. Uh, and in fact, I think this is the kind of thing that we want the money skill to be able to not only do, but like kind of keep up to date and keep track of so that we can update it periodically. [...] you could kind of think of a koku as being about $10,000, not in the sense of what you can buy with it, but in the sense of like, how big a deal would it be if you suddenly got this much money? [...] PPP is kind of this way in the real world.

## 2026-10-18, third message (the approval)

> I do approve of you making a diagram tooling change that adds the issue watch file and a diagram feature for the money research section of the research record. 40 gallons was my recollection of the amount of rice, for what it's worth. Uh, I don't actually know if that's what Chris was using, but I think that you can look at the purchasing power parity spreadsheet and then actually find that out for sure. If I wanted to hand off work to the GM assistant repo for actually making the money skill, because I agree that that is where the skill belongs, then should I just tell it to look at that digest file?
