import praw
import datetime
from datetime import timezone
import database
import settings
from psaw import PushshiftAPI

api = PushshiftAPI()
reddit = praw.Reddit(client_id=settings.reddit_client_id,
                     client_secret=settings.reddit_client_secret, password=settings.reddit_client_password,
                     user_agent=settings.reddit_client_user_agent, username=settings.reddit_client_username)



class Submission():
    def __init__(self, subredditid, submission_id, subreddit, permalink, link, title, author, upvotes, downvotes, amountcomments, comments, self_text, timecreated, timegathered, visited, alreadyIn):
        self.subredditid = subredditid
        self.subreddit = subreddit
        self.permalink = permalink
        self.submission_id = submission_id
        self.link = link
        self.title = title
        self.author = author
        self.upvotes = upvotes
        self.downvotes = downvotes
        self.amountcomments = amountcomments
        self.comments = comments
        self.self_text = self_text
        self.timecreated = timecreated
        self.timegathered = timegathered
        self.visited = visited
        self.update = alreadyIn
        pass

class CommentWrapper():
    def __init__(self, text):
        self.text = text


def getPostByUrl(urlin):
    alreadyIn = False
    submission = reddit.submission(url=urlin)
    all_scripts = database.getScriptIds()
    if submission.id in [scriptid[1] for scriptid in all_scripts]:
        index = [scriptid[1] for scriptid in all_scripts].index(submission.id)
        if [scriptstatus[2] for scriptstatus in all_scripts][index] == "RAW":
            print("Script already in database, updating old script")
            alreadyIn = True
        else:
            print("Script already complete, skipping")

    comments = []
    amountReplies = settings.reddit_replies_per_comment
    try:
        for commentThread in range(0, settings.reddit_comments_per_post, 1):
            try:
                threadcomments = ()
                thread = submission.comments[commentThread]
                text = thread.body
                author = thread.author.name
                ups = thread.ups
                if author is None:
                    author = "deleted"
                if text is None:
                    text = '[deleted]'
                threadcomments = threadcomments + ((author, text, ups),)
                prevreply = thread
                for i in range(0, amountReplies, 1):
                    try:
                        reply = list(prevreply.replies)[0]
                        try:
                            text = reply.body
                            author = reply.author.name
                            ups = reply.ups
                            if author is None:
                                author = "deleted"
                            if text is None:
                                text = '[deleted]'
                            threadcomments = threadcomments + ((author, text, ups),)
                        except AttributeError:
                            continue
                        prevreply = reply
                    except IndexError:
                        continue
                comments.append(threadcomments)
            except (IndexError, AttributeError):
                pass
    except Exception:
        print("Error parsing script, skipping")

    time_created = (datetime.datetime.fromtimestamp(submission.created_utc).replace(tzinfo=timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S"))
    now = datetime.datetime.now()
    time_gathered = now.strftime('%Y-%m-%d %H:%M:%S')
    post_body = ""
    self_text = []
    test = []
    post_body = submission.selftext
    self_text = post_body.split("\n\n")
    newSub = Submission(submission.subreddit_id, submission.id, submission.subreddit.display_name, submission.permalink, submission.url,
                        submission.title, submission.author.name,
                        submission.ups, submission.downs, submission.num_comments, comments, self_text, time_created,
                        time_gathered,
                        submission.visited, alreadyIn)
    return newSub

def getInfo2():
    keyword = 'wife'
    subredditname = 'cheating_stories'
    amount = 0
    all_scripts = database.getScriptIds()
    subs = []
    posts = []
    submissions = list(api.search_submissions(q=keyword, subreddit=subredditname, limit=amount, filter=['full_link', 'selftext']))
    post_count = 0
    for url in submissions:
        #paragraphs = url[2].split('\n\n')
        post = reddit.submission(url=url[1])
        posts.append(post)
        #if len(paragraphs) < 8:
            #continue
        #else:
            #print('post meets criteria')
            #posts.append(post)
    print(len(posts))
    for x, submission in enumerate(posts):
        post_body = ""
        self_text = []
        post_body = submission.selftext
        self_text = post_body.split("\n\n")
        alreadyIn = False
        print("%s/%s" % (x + 1, len(posts)))
        if len(self_text) < 8:
            print(f"Too little paragraphs ({len(self_text)})")
            continue
        if submission.id in [scriptid[1] for scriptid in all_scripts]:
            index = [scriptid[1] for scriptid in all_scripts].index(submission.id)
            if [scriptstatus[2] for scriptstatus in all_scripts][index] == "RAW":
                print("Script already in database, updating old script")
                alreadyIn = True
            else:
                print("Script already complete, skipping")
                continue
        comments = []
        amountReplies = settings.reddit_replies_per_comment
        try:
            for commentThread in range(0, settings.reddit_comments_per_post, 1):
                try:
                    threadcomments = ()
                    thread = submission.comments[commentThread]
                    text = thread.body
                    author = thread.author.name
                    ups = thread.ups
                    if author is None:
                        author = "deleted"
                    if text is None:
                        text = '[deleted]'
                    threadcomments = threadcomments + ((author, text, ups),)
                    prevreply = thread
                    for i in range(0, amountReplies, 1):
                        try:
                            reply = list(prevreply.replies)[0]
                            try:
                                text = reply.body
                                author = reply.author.name
                                ups = reply.ups
                                if author is None:
                                    author = "deleted"
                                if text is None:
                                    text = '[deleted]'
                                threadcomments = threadcomments + ((author, text, ups),)
                            except AttributeError as e:
                                continue
                            prevreply = reply
                        except IndexError:
                            continue
                    comments.append(threadcomments)
                except (IndexError, AttributeError) as e:
                    pass
        except Exception:
            print("Error parsing script, skipping")
            continue

        if not alreadyIn:
            print(f"Submission good to add ({len(self_text)})")

        now = datetime.datetime.now()
        author = str(submission.author)
        time_created = (datetime.datetime.fromtimestamp(submission.created_utc).replace(tzinfo=timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"))
        time_gathered = now.strftime('%Y-%m-%d %H:%M:%S')
        newSub = Submission(submission.subreddit_id, submission.id, subredditname, submission.permalink, submission.url,
                            submission.title, author,
                            submission.ups, submission.downs, submission.num_comments, comments, self_text,
                            time_created, time_gathered,
                            submission.visited, alreadyIn)
        subs.append(newSub)
    return subs




def getInfo(subredditname, amount):
    all_scripts = database.getScriptIds()
    subs = []
    subreddit = reddit.subreddit(subredditname)
    #hot_subreddit = subreddit.hot(limit=amount)
    hot_subreddit = subreddit.search("wife cheat", sort='relevance', time_filter='all', limit=amount)
    #hot_subreddit = subreddit.top(time_filter='all', limit=amount)
    for x, submission in enumerate(hot_subreddit):
        post_body = ""
        self_text = []
        post_body = submission.selftext
        self_text = post_body.split("\n\n")
        alreadyIn = False
        print("%s/%s" % (x + 1, amount))
        if len(self_text) < 8:
            print(f"Too little paragraphs ({len(self_text)})")
            continue
        if submission.id in [scriptid[1] for scriptid in all_scripts]:
            index = [scriptid[1] for scriptid in all_scripts].index(submission.id)
            if [scriptstatus[2] for scriptstatus in all_scripts][index] == "RAW":
                print("Script already in database, updating old script")
                alreadyIn = True
            else:
                print("Script already complete, skipping")
                continue
        comments = []
        amountReplies = settings.reddit_replies_per_comment
        try:
            for commentThread in range(0, settings.reddit_comments_per_post, 1):
                try:
                    threadcomments = ()
                    thread = submission.comments[commentThread]
                    text = thread.body
                    author = thread.author.name
                    ups = thread.ups
                    if author is None:
                        author = "deleted"
                    threadcomments = threadcomments + ((author, text, ups),)
                    prevreply = thread
                    for i in range(0, amountReplies, 1):
                        try:
                            reply = list(prevreply.replies)[0]
                            try:
                                text = reply.body
                                author = reply.author.name
                                ups = reply.ups
                                threadcomments = threadcomments + ((author, text, ups),)
                            except AttributeError as e:
                                continue
                            prevreply = reply
                        except IndexError:
                            continue
                    comments.append(threadcomments)
                except (IndexError, AttributeError) as e:
                    pass
        except Exception:
            print("Error parsing script, skipping")
            continue

        if not alreadyIn:
            print(f"Submission good to add ({len(self_text)})")

        now = datetime.datetime.now()
        author = str(submission.author)
        time_created = (datetime.datetime.fromtimestamp(submission.created_utc).replace(tzinfo=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
        time_gathered = now.strftime('%Y-%m-%d %H:%M:%S')
        newSub = Submission(submission.subreddit_id, submission.id, subredditname, submission.permalink, submission.url, submission.title, author,
                            submission.ups, submission.downs, submission.num_comments, comments, self_text, time_created, time_gathered,
                            submission.visited, alreadyIn)
        subs.append(newSub)
    return subs
