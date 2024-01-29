from django.http import HttpResponse
from django.shortcuts import render
from .models import Tags, SubTags,UserSetting
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from markdown_it import MarkdownIt
from django.shortcuts import redirect

# View to create a new tab
def create_tab(request):
    if request.method == 'POST':
        tab_name = request.POST.get('tab_name')
    print(tab_name)
    tabs_with_user_subtabs = []

    if tab_name:  # Check to ensure tab_name is not empty
        new_tab = Tags.objects.create(name=tab_name)
        context = {'tabs': [new_tab]}
    tabs= Tags.objects.all()
    for tab in tabs:
        user_subtabs = SubTags.objects.filter(tag=tab, user=request.user)
        tabs_with_user_subtabs.append({'tab': tab, 'user_subtabs': user_subtabs})
    return HttpResponse(render_to_string('includes/tabs.html',{"tabs_with_user_subtabs":tabs_with_user_subtabs}))

# View to create a new subtab
def create_subtab(request):
    tabs_with_user_subtabs = []
    if request.method == 'POST':
        subtab_name = request.POST.get('subtab_name')
        subtab_id = request.POST.get('subtab_id')
        if subtab_name:  # Check to ensure subtab_name is not empty
            tag_instance = get_object_or_404(Tags, id=int(subtab_id))
            new_subtab = SubTags.objects.create(name=subtab_name, tag=tag_instance, user=request.user)
            new_subtab.save()
    tabs= Tags.objects.all()
    for tab in tabs:
        user_subtabs = SubTags.objects.filter(tag=tab, user=request.user)
        tabs_with_user_subtabs.append({'tab': tab, 'user_subtabs': user_subtabs})

    return HttpResponse(render_to_string('includes/tabs.html',{"tabs_with_user_subtabs":tabs_with_user_subtabs}))
            

# View to return content for a specific tab
def get_tab_content(request, tab_id):
    if request.method == 'GET':
        try:
            tab = Tags.objects.get(id=tab_id)
            subtabs = tab.subtab_set.all()
            return render(request, 'partials/tab_content.html', {'tab': tab, 'subtabs': subtabs})
        except Tags.DoesNotExist:
            return HttpResponse("Error: Tab not found", status=404)
    return HttpResponse("Error: Invalid Request", status=400)

def home(request):
    tabs = Tags.objects.all()
    tabs_with_user_subtabs = []
    user_settings = UserSetting.objects.get(user=request.user)

    for tab in tabs:
        # Get SubTags related to the current tag and the current user
        user_subtabs = SubTags.objects.filter(tag=tab, user=request.user)
        tabs_with_user_subtabs.append({'tab': tab, 'user_subtabs': user_subtabs})

    return render(request, 'tab_menu.html', {'tabs_with_user_subtabs': tabs_with_user_subtabs,'edit':user_settings.edit_mode})


def get_subtab(request,subtab_id):
    if request.method == 'GET':
        try:
            settings = UserSetting.objects.get(user=request.user)

            subtab = SubTags.objects.get(id=subtab_id)
            if settings.edit_mode:
                subtab = SubTags.objects.get(id=subtab_id)
                return HttpResponse(subtab.markdown)
            else:

                md = MarkdownIt()
                tokens  = process_tokens(md, subtab.markdown)

                html_content = md.renderer.render(tokens, md.options, {})
                return HttpResponse(render_to_string('markdown.html', {'html_content': html_content,
                                                                       'show': False,}))

        except SubTags.DoesNotExist:
            return HttpResponse("Error: SubTab not found", status=404)
    return HttpResponse("Error: Invalid Request", status=400)

@csrf_exempt
def update_markdown(request, subtab_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            markdown = data.get('markdown')

            subtab = SubTags.objects.get(id=subtab_id)
            subtab.markdown = markdown
            subtab.save()
            return HttpResponse("Success")
        except SubTags.DoesNotExist:
            return HttpResponse("Error: SubTab not found", status=404)
    return HttpResponse("Error: Invalid Request", status=400)





def process_tokens(md, markdown_content):
    env = {}
    tokens = md.parse(markdown_content, env)
    for token in tokens:
        if token.type == "bullet_list_open" or token.type == "ordered_list_open":
            token.attrSet("class", "task-list")
        elif token.type == "fence":
            lang = token.info.strip()
            if lang:
                print(lang)
                if lang.strip() == "mermaid":
                    token.attrSet("class", "mermaid")
                else:
                    # add parent class 'hljs
                    token.attrJoin("class", "hljs")
                    token.attrSet("class", f"language-{lang}")
    return tokens

@csrf_exempt
def toggle_edit_mode(request):
    if request.method == 'GET':
        try:
            redirect_url = request.GET.get('redirect')
            settings = UserSetting.objects.get(user=request.user)
            settings.edit_mode = not settings.edit_mode
            settings.save()
            return redirect(redirect_url)
        except UserSetting.DoesNotExist:
            return HttpResponse("Error: UserSetting not found", status=404)
    return HttpResponse("Error: Invalid Request", status=400)


def home_subtab(request, subtab_id):
    if request.method=='GET':
        tabs = Tags.objects.all()
        tabs_with_user_subtabs = []
        settings = UserSetting.objects.get(user=request.user)
        for tab in tabs:
            # Get SubTags related to the current tag and the current user
            user_subtabs = SubTags.objects.filter(tag=tab, user=request.user)
            tabs_with_user_subtabs.append({'tab': tab, 'user_subtabs': user_subtabs})

        subtab = SubTags.objects.get(id=subtab_id)
        markdown_value = subtab.markdown
        if not settings.edit_mode:
            md = MarkdownIt()
            tokens = process_tokens(md, subtab.markdown)
            html_content = md.renderer.render(tokens, md.options, {})
            html_content = render_to_string('markdown.html', {'html_content': html_content,
                                                               'show': False,})
            markdown_value = html_content
        return render(request, 'tab_menu.html', {'markdown_value': markdown_value,'tabs_with_user_subtabs': tabs_with_user_subtabs,'edit':settings.edit_mode})

