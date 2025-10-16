import re
import os

# Comprehensive mapping from Salesforce DX folder structure to Metadata API types.
TYPE_MAP = {
    # 'actionPlans': 'ActionPlanTemplate',
    # 'analytics': 'Analytics',
    # 'appMenus': 'AppMenu',
    'applications': 'CustomApplication',
    'approvalProcesses':'ApprovalProcess',
    'assignmentRules': 'AssignmentRules',
    'audience':'Audience',
    'aura': 'AuraDefinitionBundle',
    # 'autoResponseRules': 'AutoResponseRules',
    # 'bots': 'Bot',
    'cachePartitions':'PlatformCachePartition',
    'classes': 'ApexClass',
    # 'community': 'CustomSite',
    # 'components': 'ApexComponent',
    'contentassets': 'ContentAsset',
    'cspTrustedSites':'CspTrustedSite',
    'customMetadata': 'CustomMetadata',
    'customPermissions': 'CustomPermission',
    'dashboards': 'Dashboard',
    # 'dataSources': 'ExternalDataSource',
    'documentGenerationSettings':'DocumentGenerationSetting',
    'duplicateRules':'DuplicateRule',
    'email': 'EmailTemplate',
    # 'escalationRules': 'EscalationRules',
    'entitlementProcesses':'EntitlementProcess',
    'experiences':'ExperienceBundle',
    'externalServiceRegistrations':'ExternalServiceRegistration',
    'flexipages':'FlexiPage',
    'flows': 'Flow',
    # 'globalValueSetTranslations': 'GlobalValueSetTranslation',
    'globalValueSets': 'GlobalValueSet',
    'groups': 'Group',
    # 'homePages': 'HomePageLayout',
    'labels': 'CustomLabels',
    'layouts': 'Layout',
    # 'letterheads': 'Letterhead',
    'lwc': 'LightningComponentBundle',
    'matchingRules': 'MatchingRules',
    'messageChannels':'LightningMessageChannel',
    'milestoneTypes':'MilestoneType',
    'mutingpermissionsets':'MutingPermissionSet',
    'navigationMenus':'NavigationMenu',
    'networks': 'Network',
    'notificationtypes':'CustomNotificationType',
    'objects': 'CustomObject', # Special case handled below
    'objectTranslations':'CustomObjectTranslation',
    'OmniInteractionConfig':'OmniInteractionConfig',
    'pages': 'ApexPage',
    'pathAssistants': 'PathAssistant',
    'permissionsetgroups':'PermissionSetGroup',
    'permissionsets': 'PermissionSet',
    'platformEventChannelMembers':'PlatformEventChannelMember',
    'profiles': 'Profile',
    'queueRoutingConfigs':'QueueRoutingConfig',
    'queues': 'Queue',
    'quickActions': 'QuickAction',
    'recordActionDeployments':'RecordActionDeployment',
    'relationshipGraphDefinitions':'RelationshipGraphDefinition',
    'remoteSiteSettings':'RemoteSiteSetting',
    'reports':'Report',
    'reportTypes':'ReportType',
    'roles': 'Role',
    'servicePresenceStatuses':'ServicePresenceStatus',
    'settings':'Settings',
    'sharingRules': 'SharingRules',
    'sharingSets':'SharingSet',
    'siteDotComSites':'SiteDotCom',
    'sites':'CustomSite',
    'skills':'Skill',
    'standardValueSets':'StandardValueSet',
    'staticresources':'StaticResource',
    'tabs': 'CustomTab',
    # 'topicsForObjects': 'TopicsForObjects',
    'translations': 'Translations',
    'triggers': 'ApexTrigger',
    'wave':'WaveDataflow',
    'workflow': 'Workflow',
    'workSkillRoutings':'WorkSkillRouting'
}

# Map for sub-folders inside the 'objects' directory
OBJECT_SUBFOLDER_MAP = {
    'businessProcesses': 'BusinessProcess',
    'compactLayouts': 'CompactLayout',
    'fields': 'CustomField',
    'fieldSets': 'FieldSet',
    'listViews': 'ListView',
    'recordTypes': 'RecordType',
    'validationRules': 'ValidationRule',
    'webLinks': 'WebLink',
    # Add more object sub-types here as needed
}

def get_object_metadata(object_name, sub_path):
    sub_parts = sub_path.split('/')
    sub_folder = sub_parts[0]
    
    metadata_type = OBJECT_SUBFOLDER_MAP.get(sub_folder)
    
    if metadata_type:
        name_with_extension = sub_parts[-1] 
        name = os.path.splitext(name_with_extension)[0]
        clean_name = re.sub(r'\.\w+-meta$', '', name)
        
        return metadata_type, f"{object_name}.{clean_name}"
    
    # Handle the main object-meta.xml file
    if sub_path.endswith('.object-meta.xml'):
        return 'CustomObject', object_name
        
    return None, None

def get_metadata_info(file_path):
    """
    Given a file path in a Salesforce DX project, returns its Metadata API type and name.
    """
    if 'force-app/main/default' not in file_path:
        return None, None
    
    # Use regex for robust path matching
    match = re.search(r'force-app/main/default/([^/]+)/(.+)$', file_path)
    if not match:
        return None, None
        
    folder, rest_of_path = match.groups()
    
    metadata_type = TYPE_MAP.get(folder)
    
    if folder in ['lwc', 'aura']:
        # For LWC and Aura, the name is the folder name
        component_name = rest_of_path.split('/')[0]
        return metadata_type, component_name

    if folder == 'objects':
        # Delegate to a specific function for objects
        obj_match = re.search(r'objects/([^/]+)/(.+)$', file_path)
        if obj_match:
            object_name = obj_match.groups()[0]
            sub_path = file_path.split(f'objects/{object_name}/')[1]
            return get_object_metadata(object_name, sub_path)

    # For other types, the name is the filename without extension
    if metadata_type:
        if folder in ['email', 'dashboards', 'reports']:
            name = os.path.splitext(rest_of_path)[0].split('.')[0]
            return metadata_type, name.replace(os.sep, '/')

        # For all other types, the name is the filename without extension
        name = os.path.splitext(rest_of_path.split('/')[-1])[0]
        if folder in ['customMetadata']:
            name = name.split('.md')[0]
        else:
            name = name.split('.')[0]
        return metadata_type, name
    
    return None, None
