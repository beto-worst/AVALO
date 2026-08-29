from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from .models import Ticket, TicketCategory, TicketSubCategory, TicketComment, TicketStatus, TicketPriority, client_list
from django.contrib.auth.models import User
from django.db.models import Q, OuterRef
from django.utils.html import strip_tags

# from django.db.models.functions import Coalesce
from django.db.models import F, Subquery
from django.http import HttpResponse  #, HttpResponseRedirect


def is_member(user):
    """Check if user is member of group 'apoyo', return True or False, used in @user_passes_test decorator"""
    # return user.groups.filter(name="apoyo").exists()
    return User.objects.filter(groups__name__in=['apoyo', 'administrador']).exists()


@login_required(login_url="login")
def index(request):
    categoies = (TicketCategory.objects.order_by("name").values_list("id", "name").distinct())
    ticket_status = TicketStatus.get_default_status(self=None)

    def get_tickets_and_latest_comments(user):
        # Get all tickets for the user
        tickets = Ticket.objects.filter(creator=user)
        # Get the latest comment for each ticket
        latest_comments = TicketComment.objects.filter(
            ticket=OuterRef('pk')
            ).order_by('-created_at')
        # Join with TicketStatus to get the status name
        tickets = tickets.annotate(
            status_name=F('status__name'),
            latest_comment=Subquery(latest_comments.values('created_at')[:1])
        ).values('id', 'title', 'status_name', 'latest_comment', 'created_at')

        return tickets.order_by('-latest_comment')

    context = {
        "tickets": get_tickets_and_latest_comments(request.user),
        "categories": categoies,
    }

    if request.htmx and request.method == "POST":
        category = request.POST.get("selected_category")
        selected_subcategory = request.POST.get("selected_subcategory")
        selected_category = TicketCategory.objects.get(id=category)
        description = f"{selected_category.name} - {selected_subcategory}"

        if selected_client := request.POST.get("selected_client"):
            description = f"{selected_category.name} - {selected_subcategory} - {selected_client}"

        title = f"{description[:25]} ..."

        Ticket.objects.create(
            title=title,
            creator=request.user,
            description=description,
            status=ticket_status,
            category_id=int(category),
        )
        return render(request, "TicketingSystem/partials/htmx_index_core.html", context)

    return render(request, "TicketingSystem/index.html", context)


@login_required(login_url="login")
def index_htmx(request):
    """ HTMX view for index.html """
    if not request.htmx or request.method != "GET":
        return HttpResponse("<html><body>ERROR: request out of context</body></html>")

    htmx_category = request.GET.get("selected_category")
    if htmx_category != "" and int(htmx_category) != 1:  # htmx_category is not empty and is not "Técnica"
        subcategories = TicketSubCategory.objects.filter(category=htmx_category)
        context = {"subcategories": subcategories, "is_category_selected": True}

    elif htmx_category == "":
        context = {"is_category_selected": False}

    else:
        subcategories = TicketSubCategory.objects.filter(category=htmx_category)
        clients = client_list(request.user.id).order_by('nombre')
        context = {"subcategories": subcategories,
                    "client_list": clients,
                    "es_tecnica": True,
                    "is_category_selected": True}
    return render(request, 'TicketingSystem/partials/htmx_subcategory.html', context)


@login_required(login_url="login")
def ticket_by_id(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    ticket_comments = TicketComment.objects.filter(
        ticket=ticket_id
    )  # .order_by('-created_at')

    if request.htmx and request.method == "GET":
        comment = request.GET.get("comment")
        comment = strip_tags(comment)
        TicketComment.objects.create(
            ticket=ticket, creator_comment=request.user, comment=comment
        )
        return render(
            request,
            "TicketingSystem/partials/htmx_comment_lst.html",
            {
                "ticket": ticket,
                "ticket_comments": ticket_comments,
                "ticket_id": ticket_id,
            },
        )

    return render(
        request,
        "TicketingSystem/ticket_by_id.html",
        {"ticket": ticket, "ticket_comments": ticket_comments, "ticket_id": ticket_id},
    )


# Admin section below ---------------------------------------------------------


@login_required(login_url="login")
@user_passes_test(is_member, login_url="login")
def ticket_admin(request):
    # ('title', 'creator', 'assignee', 'category', 'status', 'priority', 'description', 'created_at', 'updated_at')
    table_categories = (
        "título",
        "creador",
        "asignado",
        "categoría",
        "estado",
        "prioridad",
        "creado",
    )
    tickets = Ticket.objects.all().order_by("-created_at")
    all_categories = (
        TicketCategory.objects.order_by("name").values_list("id", "name").distinct()
    )
    all_creators = Ticket.objects.all().distinct()
    all_staff = User.objects.filter(groups__name__in=['apoyo'])
    all_status = (
        TicketStatus.objects.all().order_by("name").values_list("id", "name").distinct()
    )
    all_priorities = TicketPriority.choices

    context = {
        "tickets": tickets,
        "all_creators": all_creators,
        "table_categories": table_categories,
        "all_staff": all_staff,
        "all_categories": all_categories,
        "all_status": all_status,
        "all_priorities": all_priorities,
    }

    if request.htmx:
        if request.method == "GET":
            ticket_id = request.GET.get("_ticket_id")

            def ticket_by_id(ticket_id):
                return Ticket.objects.get(pk=ticket_id)

            if selected_staff := request.GET.get("selected_staff"):
                ticket = ticket_by_id(ticket_id)
                ticket.assignee = User.objects.get(id=selected_staff)
                ticket.save()
            elif selected_category := request.GET.get("selected_category"):
                ticket = ticket_by_id(ticket_id)
                ticket.category = TicketCategory.objects.get(id=selected_category)
                ticket.save()
            elif selected_status := request.GET.get("selected_status"):
                ticket = ticket_by_id(ticket_id)
                ticket.status = TicketStatus.objects.get(id=selected_status)
                ticket.save()
            elif selected_priority := request.GET.get("selected_priority"):
                ticket = ticket_by_id(ticket_id)
                ticket.priority = selected_priority
                ticket.save()
            return redirect(request.META["HTTP_REFERER"])

        if request.method == "POST":
            filter_creator = request.POST.get('filter_creator', None)
            filter_assignee = request.POST.get('filter_assignee', None)
            filter_category = request.POST.get('filter_category', None)
            filter_priority = request.POST.get('filter_priority', None)
            filter_status = request.POST.get('filter_status', None)
            # filter_date_range = request.POST.get('filter_date_range', None)

            query = Q()
            if filter_creator:
                query &= Q(creator=filter_creator)
            if filter_assignee:
                query &= Q(assignee=filter_assignee)
            if filter_category:
                query &= Q(category=filter_category)
            if filter_priority:
                query &= Q(priority=filter_priority)
            if filter_status:
                query &= Q(status=filter_status)
            # if filter_date_range:
            #     query &= Q(created_at__range=[filter_date_range[0], filter_date_range[1]])

            ticket_filter = Ticket.objects.filter(query).order_by("-created_at")

            context = {
                "tickets": ticket_filter,
                "table_categories": table_categories,
                "all_staff": all_staff,
                "all_categories": all_categories,
                "all_status": all_status,
                "all_priorities": all_priorities,
            }
            return render(request, "TicketingSystem/partials/htmx_tai_lst.html", context)

    return render(request, "TicketingSystem/ticket_admin_index.html", context)


@login_required(login_url="login")
@user_passes_test(is_member, login_url="login")
def ticket_admin_edit(request, ticket_id=None):
    if ticket_id is not None:
        ticket = Ticket.objects.get(pk=ticket_id)
        ticket_comments = TicketComment.objects.filter(ticket=ticket_id)
    else:
        ticket = None
        ticket_comments = None

    table_categories = (
        "creador",
        "asignado",
        "categoría",
        "estado",
        "prioridad",
        "creado",
    )
    all_categories = (
        TicketCategory.objects.order_by("name").values_list("id", "name").distinct()
    )
    all_staff = User.objects.filter(is_staff=True)
    all_status = (
        TicketStatus.objects.all().order_by("name").values_list("id", "name").distinct()
    )
    all_priorities = TicketPriority.choices

    context = {
        "ticket_id": ticket_id,
        "ticket": ticket,
        "ticket_comments": ticket_comments,
        "table_categories": table_categories,
        "all_staff": all_staff,
        "all_categories": all_categories,
        "all_status": all_status,
        "all_priorities": all_priorities,
    }

    if request.htmx and request.method == "GET":
        ticket_id = request.GET.get("_ticket_id")

        def ticket_by_id(ticket_id):
            return Ticket.objects.get(pk=ticket_id)

        if selected_staff := request.GET.get("selected_staff"):
            ticket = ticket_by_id(ticket_id)
            ticket.assignee = User.objects.get(id=selected_staff)
            ticket.save()
        elif selected_category := request.GET.get("selected_category"):
            ticket = ticket_by_id(ticket_id)
            ticket.category = TicketCategory.objects.get(id=selected_category)
            ticket.save()
        elif selected_status := request.GET.get("selected_status"):
            ticket = ticket_by_id(ticket_id)
            ticket.status = TicketStatus.objects.get(id=selected_status)
            ticket.save()
        elif selected_priority := request.GET.get("selected_priority"):
            ticket = ticket_by_id(ticket_id)
            ticket.priority = selected_priority
            ticket.save()
        elif comment := request.GET.get("comment"):
            ticket = ticket_by_id(ticket_id)
            TicketComment.objects.create(
                ticket=ticket, creator_comment=request.user, comment=comment
            )
            return render(
                request, "TicketingSystem/partials/htmx_tae_comments.html", context
            )
        return redirect(request.META["HTTP_REFERER"])

    return render(request, "TicketingSystem/ticket_admin_edit.html", context)
