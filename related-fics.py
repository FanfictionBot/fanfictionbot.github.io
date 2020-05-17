import psaw
import progressbar
import re
from collections import defaultdict, namedtuple
import argparse
import json

api = psaw.PushshiftAPI()
comment_regex = re.compile(r"""\[\*\*\*(?P<name>.+)\*\*\*\].+fanfiction.net\/s\/(?P<id>\d+)""")
FicComment = namedtuple('FicComment', ['name', 'id', 'score', 'permalink'])


def get_comment_mapping(author: str, num_comments: int):
    fic_id_to_submissions, submissions_to_fics = defaultdict(set), defaultdict(set)
    bar = progressbar.ProgressBar(max_value=num_comments)
    errors = []

    for i, comment in enumerate(
            api.search_comments(author=author,
                                filter=['score', 'id', 'link_id', 'body', 'permalink'],
                                limit=num_comments)):
        bar.update(i)
        for fic_name, fic_id in re.findall(comment_regex, comment.body):
            try:
                # Validate that all attributes exist (some of these will not for removed/deleted submissions)
                _, _, _, _, _ = comment.score, comment.id, comment.link_id, comment.body, comment.permalink
                fic_name = fic_name.replace("\\", "")
                f = FicComment(name=fic_name, id=fic_id, score=comment.score, permalink=comment.permalink)
                fic_id_to_submissions[fic_id].add(comment.link_id)
                submissions_to_fics[comment.link_id].add(f)
            except Exception as e:
                errors.append(str(e))
                continue
    bar.finish()

    if len(errors) > 0:
        print("Errors:\n" + "\n".join(errors))
        print(f"{len(errors)} errors.")
    return fic_id_to_submissions, submissions_to_fics


def to_json(mapping):
    def set_default(obj):
        if isinstance(obj, set):
            return list(obj)
        raise TypeError
    return json.dumps(mapping, default=set_default)


def write_js_data(author: str, num_comments: int, js_path: str):
    fic_id_to_submissions, submissions_to_fics = get_comment_mapping(author, num_comments)
    with open(js_path, "w") as text_file:
        text_file.write("data = " + to_json({
            "fic_id_to_submissions": fic_id_to_submissions,
            "submissions_to_fics": submissions_to_fics,
        }))
    print(f"Saved {len(fic_id_to_submissions)} fics across {len(submissions_to_fics)} submissions.")


def main():
    args = argparse.ArgumentParser()
    args.add_argument("--js-path", type=str, help="location of js comment mapping", default="recs/script/data.js")
    args.add_argument("--author", type=str, help="username that FanfictionBot is operating under",
                      default="FanfictionBot")
    args.add_argument("--num-comments", type=int, help="number of comments; default will determine maximum", default=0)
    parsed = args.parse_args()

    num_comments = parsed.num_comments
    if not parsed.num_comments:
        num_comments = sum(api.redditor_subreddit_activity(parsed.author)['comment'].values())
    write_js_data(parsed.author, num_comments, parsed.js_path)


if __name__ == '__main__':
    main()
