from django.urls import path, include
from datamad2 import views

urlpatterns = [

    # Home
    path('', views.FacetedGrantListView.as_view(), name='grant_list'),

    # Search result export
    path('export', views.SearchResultsExportView.as_view(), name='results_export'),

    # Django account management
    path('accounts/', include('django.contrib.auth.urls',)),

    # User Account
    path('account/details', views.MyAccountDetailsView.as_view(), name='my_account'),
    path('account/preferences', views.MyAccountPreferencesView.as_view(), name='preferences'),

    # Datacentre URLs
    path('account/datacentre', (views.MyAccountDatacentreView.as_view()), name='datacentre'),
    path('account/datacentre/users', views.MyAccountUsersView.as_view(), name='user_list'),
    path('account/datacentre/users/new', (views.MyAccountNewUserView.as_view()), name='user_create'),
    path('account/datacentre/users/<int:pk>', views.MyAccountEditUserView.as_view(), name='user_update'),
    path('account/datacentre/users/<int:pk>/delete', views.MyAccountRemoveUserView.as_view(), name='user_delete'),
    path('account/datacentre/jira-issue', (views.MyAccountDatacentreIssueTypeView.as_view()), name='jira_issue_type'),
    path('account/datacentre/github-issue', (views.MyAccountDatacentreIssueTypeView.as_view()), name='github_issue_type'),

    path('account/datacentre/templates', (views.DocumentTemplateListView.as_view()), name='document_template_list'),
    path('account/datacentre/templates/new', (views.DocumentTemplateCreateView.as_view()), name='document_template_create'),
    path('account/datacentre/templates/<int:pk>', (views.DocumentTemplateUpdateView.as_view()), name='document_template_update'),
    path('account/datacentre/templates/<int:pk>/delete', (views.DocumentTemplateDeleteView.as_view()), name='document_template_delete'),
    path('account/datacentre/data_formats', (views.DataFormatListView.as_view()), name='data_format_list'),
    path('account/datacentre/data_formats/new', (views.DataFormatUpdateCreateView.as_view()), name='data_format_create'),
    path('account/datacentre/data_formats/<int:pk>', (views.DataFormatUpdateCreateView.as_view()), name='data_format_update'),
    path('account/datacentre/data_formats/<int:pk>/delete', (views.DataFormatDeleteView.as_view()), name='data_format_delete'),
    path('account/datacentre/preservation_plans', (views.PreservationPlanListView.as_view()), name='preservation_plan_list'),
    path('account/datacentre/preservation_plans/new', (views.PreservationPlanUpdateCreateView.as_view()), name='preservation_plan_create'),
    path('account/datacentre/preservation_plans/<int:pk>', (views.PreservationPlanUpdateCreateView.as_view()), name='preservation_plan_update'),
    path('account/datacentre/preservation_plans/<int:pk>/delete', (views.PreservationPlanDeleteView.as_view()), name='preservation_plan_delete'),
    path('account/datacentre/jirasubtasks', (views.JIRASubtaskListView.as_view()),name='JIRAsubtask_list'),
    path('account/datacentre/jirasubtasks/new', (views.JIRASubtaskUpdateCreateView.as_view()),name='JIRAsubtask_create'),
    path('account/datacentre/jirasubtasks/<int:pk>', (views.JIRASubtaskUpdateCreateView.as_view()),name='JIRAsubtask_update'),
    path('account/datacentre/jirasubtasks/<int:pk>/delete', (views.JIRASubtaskDeleteView.as_view()),name='JIRAsubtask_delete'),
    path('account/datacentre/githubsubtasks', (views.GithubSubtaskListView.as_view()),name='Githubsubtask_list'),
    path('account/datacentre/githubsubtasks/new', (views.GithubSubtaskUpdateCreateView.as_view()),name='Githubsubtask_create'),
    path('account/datacentre/githubsubtasks/<int:pk>', (views.GithubSubtaskUpdateCreateView.as_view()),name='Githubsubtask_update'),
    path('account/datacentre/githubsubtasks/<int:pk>/delete', (views.GithubSubtaskDeleteView.as_view()),name='Githubsubtask_delete'),

    # Grant URLs
    path('grant/<int:pk>/', views.grant_detail, name='grant_detail'),
    path('grant/<int:pk>/visibility/<str:action>', views.grant_visibility, name='grant_visibility'),
    path('grant/<int:pk>/jira_convert', views.push_to_jira, name='jira_convert'),
    path('grant/<int:pk>/github_convert', views.push_to_github, name='github_convert'),

    path('grant/<int:pk>/change_claim/', views.ChangeClaimFormView.as_view(), name='change_claim'),
    path('grant/<int:pk>/history/', views.grant_history, name='grant_history'),
    path('grant/<int:pk>/history/<int:imported_pk>', views.grant_history_detail, name='grant_history_detail'),
    path('grant/<int:pk>/edit/', views.GrantInfoEditView.as_view(), name='grantinfo_edit'),
    path('grant/<int:pk>/generate_document/', views.DocumentGenerationSelectView.as_view(), name='grant_generate_document_select'),
    path('grant/<int:pk>/dataproducts', views.DataProductView.as_view(), name='dataproduct_view'),
    path('grant/<int:pk>/dataproducts/<str:data_product_type>/new', views.DataProductUpdateCreateView.as_view(), name='dataproduct_new'),
    path('grant/<int:pk>/dataproducts/<str:data_product_type>/<int:dp_pk>', views.DataProductUpdateCreateView.as_view(), name='dataproduct_update'),
    path('grant/<int:pk>/dataproducts/<int:dp_pk>/delete', views.DataProductDeleteView.as_view(), name='dataproduct_delete'),
    path('grant/<int:pk>/jiratickets/<int:jt_pk>/delete', views.JIRATicketDeleteView.as_view(), name='jiraticket_delete'),
    path('grant/<int:pk>/githubtickets/<int:jt_pk>/delete', views.GithubTicketDeleteView.as_view(), name='githubticket_delete'),

    # Document URLs
    path('document/upload/<int:pk>', views.document_upload, name='document_upload'),
    path('document/<int:pk>/delete/', views.delete_file, name='delete_file'),
    path('document/multiple_upload/', views.multiple_document_upload, name='multi_document_upload'),
]