# Join the course organization

Labs in this course are handed out through GitHub. Before you can pick one up,
you need to be a member of the course organization. **This page is how you get
in.** It takes about a minute, and you only do it once for the whole semester.

You need two things: a GitHub account, and the **enrollment code** for your
section, which is in the Canvas announcement.

---

## 1. Get a GitHub account

Already have one? Skip to step 2. Any existing account is fine, including one
you made years ago for something else.

Otherwise, sign up at **[github.com/signup](https://github.com/signup)**. It is
free.

- Your username does not have to be your real name. It is public, it is hard to
  change later, and you may well still be using it in ten years. Pick something
  you would not mind a recruiter reading.
- Consider signing up with your `@student.csulb.edu` address so you can claim
  [GitHub Education](https://education.github.com/students), which is free and
  includes Copilot among other things. Optional, and any address works.

## 2. Open an enrollment issue

Click **[New issue](../../issues/new/choose)** and choose
**Join the course organization**.

Paste the **enrollment code** for your section into the one field, and submit.
The code is in your section's Canvas announcement and looks like
`CECS326-01-FA26-XXXX`.

> [!IMPORTANT]
> Use the code for **your** section. It is what puts you in the right
> classroom, and the sections have different codes.

You do not type your username anywhere. GitHub already knows who you are from
the account you are signed in to, which is why there is nothing here to get
wrong.

> [!WARNING]
> **This repository is public. Do not put your name, student ID, or email
> address in the issue.** None of it is needed. If you do, a bot will ask you
> to edit it out.

## 3. Accept the invitation

Within a minute or two, a bot replies to your issue and GitHub emails you an
invitation to the organization.

**Accept it.** This is the step people forget, and nothing works until you do.
If the email has not arrived after a few minutes, check spam, or go to
[github.com/orgs/Giacalone-CECS/invitation](https://github.com/orgs/Giacalone-CECS/invitation)
while signed in.

> [!CAUTION]
> **Invitations expire after 7 days.** If yours lapses, just open another issue
> with the same code and you will get a fresh one.

## 4. One more step, and it is a different one

You are in the organization for the whole semester, and you will not need to
come back to this page.

**Joining the organization is not the same as picking up a lab.** Joining you do
once. Picking up a lab is separate, and you do it once for *every* lab, with the
one-line command in that lab's Canvas announcement:

```
gh student accept Giacalone-CECS cecs-326-fa26-01 lab-01-threads
```

That command creates your own private repository for that lab. Until you run it,
you do not have one.

> [!TIP]
> **If a push ever fails with a 404**, this is almost always why. Run
> `git remote -v` in your working folder. If the address contains
> `agiacalone`, you are in my copy of the assignment, which you cannot write
> to. Your own repository has your GitHub username at the end of its name.

---

## Troubleshooting

**The bot said my code was not recognized.**
Check you copied it from the announcement for *your* section, with no extra
spaces before or after. Then open a new issue with the corrected code.

**The bot said I am already on the roster.**
You are. If you never got the invitation email or it expired, say so in that
issue and you will get another.

**The bot has not replied at all.**
Give it five minutes. If nothing happens, message me on Canvas rather than
opening more issues.

**I accepted the invitation but `gh student accept` says I am not a member.**
Give GitHub a minute to catch up, then try again. If it persists, message me.

**I want to use a different GitHub account than the one I enrolled with.**
Message me on Canvas. Do not enroll twice.

---

## What this actually does

For the curious. The issue you open triggers a
[GitHub Actions workflow](.github/workflows/enroll.yml) that checks your code
against a list, then adds the issue's author to the roster for that section and
asks GitHub to send you an organization invitation.

The author of the issue is the identity. There is no name field, no username
field, and no form to mistype, because GitHub already told the workflow who
opened the issue. That is also why nothing identifying about you needs to be
posted in public here.

Everything it does is in [`scripts/enroll.py`](scripts/enroll.py), which is
about a hundred lines and worth a read if you have not seen CI automation
before. You are welcome to look at how your own course is run.
