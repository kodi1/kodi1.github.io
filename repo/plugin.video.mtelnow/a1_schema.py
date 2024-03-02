from lib import sgqlc
from lib.sgqlc import types as types
from lib.sgqlc.types import datetime as datetime
from lib.sgqlc.types import relay as relay


a1_schema = sgqlc.types.Schema()


# Unexport Node/PageInfo, let schema re-declare them
a1_schema -= sgqlc.types.relay.Node
a1_schema -= sgqlc.types.relay.PageInfo



########################################################################
# Scalars and Enumerations
########################################################################
class AppSorting(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('MANUAL', 'AUTOMATIC')


Boolean = sgqlc.types.Boolean

class ChannelKind(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('TV', 'RADIO')


class ChannelListKind(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('FULL', 'DVB', 'OPERATOR', 'SUBSCRIBER', 'DYNAMIC')


class ChannelSortingMode(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('DEFAULT', 'REPLAY_PERMISSIONS', 'ALPHABETICAL')


class ContentDeliveryKind(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('MULTICAST', 'HLS', 'DASH', 'DVB', 'RTSP', 'HTTP')


class ContentFolderKind(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('CONTINUE_WATCHING', 'FAVOURITES', 'PURCHASES', 'RECOMMENDATION', 'RECORDINGS', 'REMINDERS', 'VOD', 'EPG', 'SEARCH')


class DVBModulationKind(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('QAM16', 'QAM32', 'QAM64', 'QAM128', 'QAM256')


Date = sgqlc.types.datetime.Date

class DeviceType(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('NATIVE_STB', 'ANDROID_STB', 'AMAZON_FIRE_TV', 'IOS_PHONE', 'ANDROID_PHONE', 'IOS_TABLET', 'ANDROID_TABLET', 'CHROMECAST', 'MACOS', 'WINDOWS_PC', 'LINUX', 'WINDOWS_PC_EDGE', 'WINDOWS_PC_INTERNET_EXPLORER', 'WINDOWS_PC_CHROME', 'WINDOWS_PC_FIREFOX', 'MACOS_SAFARI', 'MACOS_CHROME', 'MACOS_FIREFOX', 'MACOS_EDGE', 'LINUX_CHROME', 'LINUX_FIREFOX')


class EndOfStreamBehaviour(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('TO_LIVE', 'PAUSE', 'NEXT_EVENT', 'PLAY')


class EventLoggingOption(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('ALL',)


class FavouritableItemKind(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('EVENT', 'NETWORK_RECORDING', 'VOD_ASSET', 'VOD_PRODUCT')


Float = sgqlc.types.Float

class GroupInfoSelectBehaviour(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('SELECT_START', 'SELECT_END', 'SELECT_NOW')


class HybridChannelDisplayBehaviour(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('ALWAYS', 'ONLY_IF_ON_DVB')


class HybridChannelPlaybackBehaviour(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('PREFER_DVB', 'FORCE_GRAPHQL_PLAYBACK_URL', 'FORCE_DVB')


ID = sgqlc.types.ID

class ImageFlavour(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('NORMAL', 'INVERTED')


Int = sgqlc.types.Int

class MessageDisplayKind(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('INBOX', 'NOTIFICATION')


class MessageStatus(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('NEW', 'READ')


class PageWithRecommendations(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('HOME', 'SEARCH', 'ONDEMAND', 'MYLIBRARY', 'DETAILED_TV', 'DETAILED_REC', 'DETAILED_VOD_MOVIE', 'DETAILED_VOD_PRODUCT', 'DETAILED_CHANNEL', 'DETAILED_CHANNEL_PRODUCT', 'DETAILED_TV_SERIES', 'DETAILED_REC_SERIES', 'DETAILED_VOD_SERIES', 'DETAILED_MAIN_PACKAGE', 'DETAILED_FEATURE', 'DETAILED_PROMOTION')


class PincodeKind(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('MASTER', 'PROFILE')


class ProductKind(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('RENTAL', 'PURCHASE', 'SUBSCRIPTION', 'SUBSCRIPTION_UPSELLABLE', 'FREE')


class ProductPurchaseStatus(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('NOT_SUBSCRIBED', 'IN_PROGRESS', 'SUBSCRIBED')


class ProfileKind(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('FAMILY', 'KIDS', 'OTHER')


class ProfileProtection(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('NONE', 'PINCODE', 'MASTERPIN')


class QuotaKind(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('DURATION', 'STORAGE')


class RecordingKind(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('NETWORK',)


class RecordingStatus(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'INCOMPLETE', 'CONFLICT', 'FAILED')


class SearchContentType(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('EVENTS', 'RECORDINGS', 'ON_DEMAND')


class SearchPaidOrIncludedContent(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('ALL', 'PAID', 'INCLUDED')


String = sgqlc.types.String

class UpsellProductsContextKind(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('CHANNEL', 'VOD_ASSET', 'EVENT')


class VideoQuality(sgqlc.types.Enum):
    __schema__ = a1_schema
    __choices__ = ('SD', 'HD', 'UHD')



########################################################################
# Input Objects
########################################################################
class CancelNetworkSeriesRecordingInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'event_id')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    event_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='eventId')


class CancelSeasonOfNetworkSeriesRecordingInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'event_id')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    event_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='eventId')


class CancelVODTransactionInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'vod_asset_entitlement_id')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    vod_asset_entitlement_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='vodAssetEntitlementId')


class CatchupEventInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('event_id', 'replace_session_id', 'streaming_network_ip_address')
    event_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='eventId')
    replace_session_id = sgqlc.types.Field(ID, graphql_name='replaceSessionId')
    streaming_network_ip_address = sgqlc.types.Field(String, graphql_name='streamingNetworkIpAddress')


class ChangeChannelListNameInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('channel_list_id', 'name')
    channel_list_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='channelListId')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class ChangeChannelPreferencesInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'channel_id', 'audio_language', 'subtitle_language')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    channel_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='channelId')
    audio_language = sgqlc.types.Field(String, graphql_name='audioLanguage')
    subtitle_language = sgqlc.types.Field(String, graphql_name='subtitleLanguage')


class ChangeDeviceDRMNetworkDeviceIdInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('drm_network_device_id',)
    drm_network_device_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='drmNetworkDeviceId')


class ChangeDeviceEnablementPolicyInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('device_id', 'device_enablement_policy_id', 'enabled')
    device_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='deviceId')
    device_enablement_policy_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='deviceEnablementPolicyId')
    enabled = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='enabled')


class ChangeDeviceNameInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('device_id', 'name')
    device_id = sgqlc.types.Field(ID, graphql_name='deviceId')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')


class ChangeDevicePreviewModeInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('enabled',)
    enabled = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='enabled')


class ChangeHouseholdCommunityInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('community_id',)
    community_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='communityId')


class ChangeHouseholdOnboardingInfoInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('master_pincode_step_completed', 'community_step_completed', 'privacy_step_completed', 'replay_step_completed')
    master_pincode_step_completed = sgqlc.types.Field(Boolean, graphql_name='masterPincodeStepCompleted')
    community_step_completed = sgqlc.types.Field(Boolean, graphql_name='communityStepCompleted')
    privacy_step_completed = sgqlc.types.Field(Boolean, graphql_name='privacyStepCompleted')
    replay_step_completed = sgqlc.types.Field(Boolean, graphql_name='replayStepCompleted')


class ChangeHouseholdPreferencesInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('display_non_adult_content', 'track_viewing_behaviour', 'agreed_to_terms_and_conditions')
    display_non_adult_content = sgqlc.types.Field(Boolean, graphql_name='displayNonAdultContent')
    track_viewing_behaviour = sgqlc.types.Field(Boolean, graphql_name='trackViewingBehaviour')
    agreed_to_terms_and_conditions = sgqlc.types.Field(Boolean, graphql_name='agreedToTermsAndConditions')


class ChangeInitialChannelListInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'channel_list_id')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    channel_list_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='channelListId')


class ChangeLanguageInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class ChangeMasterPincodeInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('master_pincode',)
    master_pincode = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='masterPincode')


class ChangeNetworkRecordingInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'recording_id', 'delete_protected')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    recording_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='recordingId')
    delete_protected = sgqlc.types.Field(Boolean, graphql_name='deleteProtected')


class ChangeProfileOnboardingInfoInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('age_rating_step_completed',)
    age_rating_step_completed = sgqlc.types.Field(Boolean, graphql_name='ageRatingStepCompleted')


class ChangeProfilePermissionsInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'parental_rating_id', 'mask_content', 'can_purchase', 'purchase_protection', 'purchase_limit', 'display_blocked_channels', 'other_profiles_content', 'edit_my_library', 'create_recordings', 'logout_pincode', 'edit_channel_lists', 'single_channel_list_id', 'access_search', 'resort_apps', 'manage_apps')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    parental_rating_id = sgqlc.types.Field(ID, graphql_name='parentalRatingId')
    mask_content = sgqlc.types.Field(Boolean, graphql_name='maskContent')
    can_purchase = sgqlc.types.Field(Boolean, graphql_name='canPurchase')
    purchase_protection = sgqlc.types.Field(ProfileProtection, graphql_name='purchaseProtection')
    purchase_limit = sgqlc.types.Field(Float, graphql_name='purchaseLimit')
    display_blocked_channels = sgqlc.types.Field(Boolean, graphql_name='displayBlockedChannels')
    other_profiles_content = sgqlc.types.Field(Boolean, graphql_name='otherProfilesContent')
    edit_my_library = sgqlc.types.Field(Boolean, graphql_name='editMyLibrary')
    create_recordings = sgqlc.types.Field(Boolean, graphql_name='createRecordings')
    logout_pincode = sgqlc.types.Field(String, graphql_name='logoutPincode')
    edit_channel_lists = sgqlc.types.Field(Boolean, graphql_name='editChannelLists')
    single_channel_list_id = sgqlc.types.Field(ID, graphql_name='singleChannelListId')
    access_search = sgqlc.types.Field(Boolean, graphql_name='accessSearch')
    resort_apps = sgqlc.types.Field(Boolean, graphql_name='resortApps')
    manage_apps = sgqlc.types.Field(Boolean, graphql_name='manageApps')


class ChangeProfilePincodeInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'current_pincode', 'new_pincode')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    current_pincode = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='currentPincode')
    new_pincode = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='newPincode')


class ChangeProfilePreferencesInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'name', 'kind', 'protection', 'first_audio_language', 'second_audio_language', 'first_subtitle_language', 'second_subtitle_language', 'hard_of_hearing', 'visually_impaired')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    name = sgqlc.types.Field(String, graphql_name='name')
    kind = sgqlc.types.Field(ProfileKind, graphql_name='kind')
    protection = sgqlc.types.Field(ProfileProtection, graphql_name='protection')
    first_audio_language = sgqlc.types.Field(String, graphql_name='firstAudioLanguage')
    second_audio_language = sgqlc.types.Field(String, graphql_name='secondAudioLanguage')
    first_subtitle_language = sgqlc.types.Field(String, graphql_name='firstSubtitleLanguage')
    second_subtitle_language = sgqlc.types.Field(String, graphql_name='secondSubtitleLanguage')
    hard_of_hearing = sgqlc.types.Field(Boolean, graphql_name='hardOfHearing')
    visually_impaired = sgqlc.types.Field(Boolean, graphql_name='visuallyImpaired')


class ChannelFilterParams(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('household_confirmed_replay_permissions_set', 'replay_enabled', 'force_return_blocked_channels')
    household_confirmed_replay_permissions_set = sgqlc.types.Field(Boolean, graphql_name='householdConfirmedReplayPermissionsSet')
    replay_enabled = sgqlc.types.Field(Boolean, graphql_name='replayEnabled')
    force_return_blocked_channels = sgqlc.types.Field(Boolean, graphql_name='forceReturnBlockedChannels')


class ChannelSortingParams(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('mode',)
    mode = sgqlc.types.Field(ChannelSortingMode, graphql_name='mode')


class CompleteVODTransactionInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'vod_asset_entitlement_id')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    vod_asset_entitlement_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='vodAssetEntitlementId')


class CreateDeviceInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('client_generated_device_id', 'device_type', 'name', 'language_id')
    client_generated_device_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='clientGeneratedDeviceId')
    device_type = sgqlc.types.Field(sgqlc.types.non_null(DeviceType), graphql_name='deviceType')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    language_id = sgqlc.types.Field(ID, graphql_name='languageId')


class CreateNetworkRecordingInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'event_id')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    event_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='eventId')


class CreateNetworkSeriesRecordingInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'event_id')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    event_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='eventId')


class CreatePersonalChannelListInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'name', 'channels')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    channels = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(ID)), graphql_name='channels')


class CreateProfilePincodeInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'pincode')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    pincode = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='pincode')


class DeleteDeviceInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')


class DeleteEpisodesOfNetworkSeriesRecordingInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'event_id')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    event_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='eventId')


class DeleteEventBookmarkInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'event_id')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    event_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='eventId')


class DeleteProfilePincodeInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'current_pincode')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    current_pincode = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='currentPincode')


class DeleteRecordingBookmarkInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'recording_id')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    recording_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='recordingId')


class DeleteRecordingInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'recording_id')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    recording_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='recordingId')


class DeleteVODBookmarkInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'vod_asset_id')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    vod_asset_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='vodAssetId')


class FavouriteItemInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'item_id', 'item_kind')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    item_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='itemId')
    item_kind = sgqlc.types.Field(sgqlc.types.non_null(FavouritableItemKind), graphql_name='itemKind')


class FullPaginationParams(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('first', 'after', 'last', 'before')
    first = sgqlc.types.Field(Int, graphql_name='first')
    after = sgqlc.types.Field(String, graphql_name='after')
    last = sgqlc.types.Field(Int, graphql_name='last')
    before = sgqlc.types.Field(String, graphql_name='before')


class HouseholdConfirmedReplayPermission(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('channel_id', 'enabled')
    channel_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='channelId')
    enabled = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='enabled')


class MessageFilterParams(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('status', 'display_kind')
    status = sgqlc.types.Field(sgqlc.types.list_of(MessageStatus), graphql_name='status')
    display_kind = sgqlc.types.Field(sgqlc.types.list_of(MessageDisplayKind), graphql_name='displayKind')


class PauseLiveChannelInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('channel_id', 'event_id', 'paused_at', 'replace_session_id', 'streaming_network_ip_address')
    channel_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='channelId')
    event_id = sgqlc.types.Field(ID, graphql_name='eventId')
    paused_at = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name='pausedAt')
    replace_session_id = sgqlc.types.Field(ID, graphql_name='replaceSessionId')
    streaming_network_ip_address = sgqlc.types.Field(String, graphql_name='streamingNetworkIpAddress')


class PlayChannelInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('channel_id', 'replace_session_id', 'streaming_network_ip_address')
    channel_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='channelId')
    replace_session_id = sgqlc.types.Field(ID, graphql_name='replaceSessionId')
    streaming_network_ip_address = sgqlc.types.Field(String, graphql_name='streamingNetworkIpAddress')


class PlayPPVEventInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('event_id', 'replace_session_id', 'streaming_network_ip_address')
    event_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='eventId')
    replace_session_id = sgqlc.types.Field(ID, graphql_name='replaceSessionId')
    streaming_network_ip_address = sgqlc.types.Field(String, graphql_name='streamingNetworkIpAddress')


class PlayRecordingInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('recording_id', 'replace_session_id', 'streaming_network_ip_address')
    recording_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='recordingId')
    replace_session_id = sgqlc.types.Field(ID, graphql_name='replaceSessionId')
    streaming_network_ip_address = sgqlc.types.Field(String, graphql_name='streamingNetworkIpAddress')


class PlayTrailerInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('trailer_id', 'replace_session_id', 'streaming_network_ip_address')
    trailer_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='trailerId')
    replace_session_id = sgqlc.types.Field(ID, graphql_name='replaceSessionId')
    streaming_network_ip_address = sgqlc.types.Field(String, graphql_name='streamingNetworkIpAddress')


class PlayVODAssetInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('vod_asset_id', 'vod_asset_entitlement_id', 'replace_session_id', 'streaming_network_ip_address')
    vod_asset_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='vodAssetId')
    vod_asset_entitlement_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='vodAssetEntitlementId')
    replace_session_id = sgqlc.types.Field(ID, graphql_name='replaceSessionId')
    streaming_network_ip_address = sgqlc.types.Field(String, graphql_name='streamingNetworkIpAddress')


class PurchaseChannelProductInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('channel_product_id',)
    channel_product_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='channelProductId')


class PurchaseUpsellProductInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'product_id', 'price_id')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    product_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='productId')
    price_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='priceId')


class PurchaseVODProductInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'vod_product_id', 'price_id')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    vod_product_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='vodProductId')
    price_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='priceId')


class RecordingsFilterParams(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('start_date', 'end_date', 'status')
    start_date = sgqlc.types.Field(Date, graphql_name='startDate')
    end_date = sgqlc.types.Field(Date, graphql_name='endDate')
    status = sgqlc.types.Field(sgqlc.types.list_of(RecordingStatus), graphql_name='status')


class ResetProfilePreferencesInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'reset_channel_preferences')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    reset_channel_preferences = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='resetChannelPreferences')


class RestartEventInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('event_id', 'replace_session_id', 'streaming_network_ip_address')
    event_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='eventId')
    replace_session_id = sgqlc.types.Field(ID, graphql_name='replaceSessionId')
    streaming_network_ip_address = sgqlc.types.Field(String, graphql_name='streamingNetworkIpAddress')


class SearchContext(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'order_content_type')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    order_content_type = sgqlc.types.Field(SearchContentType, graphql_name='orderContentType')


class SearchFilter(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('audio_languages', 'subtitle_languages', 'minimum_rating', 'genre_ids', 'content_types', 'content_providers', 'paid_content')
    audio_languages = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='audioLanguages')
    subtitle_languages = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='subtitleLanguages')
    minimum_rating = sgqlc.types.Field(Int, graphql_name='minimumRating')
    genre_ids = sgqlc.types.Field(sgqlc.types.list_of(ID), graphql_name='genreIds')
    content_types = sgqlc.types.Field(sgqlc.types.list_of(SearchContentType), graphql_name='contentTypes')
    content_providers = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='contentProviders')
    paid_content = sgqlc.types.Field(SearchPaidOrIncludedContent, graphql_name='paidContent')


class SendPlaybackHeartbeatInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('session_id',)
    session_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='sessionId')


class SetChannelListChannelsInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('channel_list_id', 'channels')
    channel_list_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='channelListId')
    channels = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(ID)), graphql_name='channels')


class SetEventBookmarkInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'event_id', 'position', 'audio', 'subtitle')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    event_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='eventId')
    position = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='position')
    audio = sgqlc.types.Field(String, graphql_name='audio')
    subtitle = sgqlc.types.Field(String, graphql_name='subtitle')


class SetHouseholdConfirmedReplayPermissionsInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('household_confirmed_replay_permissions',)
    household_confirmed_replay_permissions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(HouseholdConfirmedReplayPermission)), graphql_name='householdConfirmedReplayPermissions')


class SetRecordingBookmarkInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'recording_id', 'position', 'audio', 'subtitle')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    recording_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='recordingId')
    position = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='position')
    audio = sgqlc.types.Field(String, graphql_name='audio')
    subtitle = sgqlc.types.Field(String, graphql_name='subtitle')


class SetVODBookmarkInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'vod_asset_id', 'position', 'audio', 'subtitle')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    vod_asset_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='vodAssetId')
    position = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='position')
    audio = sgqlc.types.Field(String, graphql_name='audio')
    subtitle = sgqlc.types.Field(String, graphql_name='subtitle')


class StartAndCompletePPVTransactionInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'ppv_product_id', 'event_id', 'price_id')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    ppv_product_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='ppvProductId')
    event_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='eventId')
    price_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='priceId')


class StartVODTransactionInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'vod_product_id', 'vod_asset_id', 'price_id')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    vod_product_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='vodProductId')
    vod_asset_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='vodAssetId')
    price_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='priceId')


class StopPlaybackInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('session_id', 'streaming_network_ip_address')
    session_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='sessionId')
    streaming_network_ip_address = sgqlc.types.Field(String, graphql_name='streamingNetworkIpAddress')


class UnfavouriteItemInput(sgqlc.types.Input):
    __schema__ = a1_schema
    __field_names__ = ('profile_id', 'item_id', 'item_kind')
    profile_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='profileId')
    item_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='itemId')
    item_kind = sgqlc.types.Field(sgqlc.types.non_null(FavouritableItemKind), graphql_name='itemKind')



########################################################################
# Output Objects and Interfaces
########################################################################
class ActiveEpisodeInfo(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('edge', 'group_id')
    edge = sgqlc.types.Field(sgqlc.types.non_null('ContentFolderContentItemsEdge'), graphql_name='edge')
    group_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='groupId')


class Cacheable(sgqlc.types.Interface):
    __schema__ = a1_schema
    __field_names__ = ('id', 'expiry')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')
    expiry = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name='expiry')


class CancelNetworkSeriesRecordingPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('events', 'quota')
    events = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('Event')), graphql_name='events')
    quota = sgqlc.types.Field('Quota', graphql_name='quota')


class CancelSeasonOfNetworkSeriesRecordingPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('events', 'quota')
    events = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('Event')), graphql_name='events')
    quota = sgqlc.types.Field('Quota', graphql_name='quota')


class CancelVODTransactionPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('success',)
    success = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='success')


class Catalog(sgqlc.types.Interface):
    __schema__ = a1_schema
    __field_names__ = ('item_count',)
    item_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='itemCount')


class CatchupEventPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('playback_info',)
    playback_info = sgqlc.types.Field(sgqlc.types.non_null('TimeshiftPlaybackInfo'), graphql_name='playbackInfo')


class ChangeChannelListNamePayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('channel_list',)
    channel_list = sgqlc.types.Field(sgqlc.types.non_null('ChannelList'), graphql_name='channelList')


class ChangeChannelPreferencesPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('channel',)
    channel = sgqlc.types.Field(sgqlc.types.non_null('Channel'), graphql_name='channel')


class ChangeDeviceDRMNetworkDeviceIdPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('device',)
    device = sgqlc.types.Field(sgqlc.types.non_null('Device'), graphql_name='device')


class ChangeDeviceEnablementPolicyPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('device',)
    device = sgqlc.types.Field(sgqlc.types.non_null('Device'), graphql_name='device')


class ChangeDeviceNamePayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('device',)
    device = sgqlc.types.Field(sgqlc.types.non_null('Device'), graphql_name='device')


class ChangeDevicePreviewModePayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('device',)
    device = sgqlc.types.Field(sgqlc.types.non_null('Device'), graphql_name='device')


class ChangeHouseholdCommunityPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('household',)
    household = sgqlc.types.Field(sgqlc.types.non_null('Household'), graphql_name='household')


class ChangeHouseholdOnboardingInfoPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('onboarding_info',)
    onboarding_info = sgqlc.types.Field('HouseholdOnboardingInfo', graphql_name='onboardingInfo')


class ChangeHouseholdPreferencesPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('household',)
    household = sgqlc.types.Field(sgqlc.types.non_null('Household'), graphql_name='household')


class ChangeInitialChannelListPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('channel_list',)
    channel_list = sgqlc.types.Field(sgqlc.types.non_null('ChannelList'), graphql_name='channelList')


class ChangeLanguagePayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('device',)
    device = sgqlc.types.Field(sgqlc.types.non_null('Device'), graphql_name='device')


class ChangeMasterPincodePayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('household',)
    household = sgqlc.types.Field(sgqlc.types.non_null('Household'), graphql_name='household')


class ChangeNetworkRecordingPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('recording',)
    recording = sgqlc.types.Field(sgqlc.types.non_null('NetworkRecording'), graphql_name='recording')


class ChangeProfileOnboardingInfoPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('onboarding_info',)
    onboarding_info = sgqlc.types.Field('ProfileOnboardingInfo', graphql_name='onboardingInfo')


class ChangeProfilePermissionsPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('profile',)
    profile = sgqlc.types.Field(sgqlc.types.non_null('Profile'), graphql_name='profile')


class ChangeProfilePincodePayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('profile',)
    profile = sgqlc.types.Field(sgqlc.types.non_null('Profile'), graphql_name='profile')


class ChangeProfilePreferencesPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('profile',)
    profile = sgqlc.types.Field(sgqlc.types.non_null('Profile'), graphql_name='profile')


class CompleteVODTransactionPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('asset',)
    asset = sgqlc.types.Field(sgqlc.types.non_null('VODAsset'), graphql_name='asset')


class Connection(sgqlc.types.Interface):
    __schema__ = a1_schema
    __field_names__ = ('page_info', 'total_count')
    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')
    total_count = sgqlc.types.Field(Int, graphql_name='totalCount')


class CreateDevicePayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('success', 'reauthenticate')
    success = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='success')
    reauthenticate = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='reauthenticate')


class CreateNetworkRecordingPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('recording', 'quota')
    recording = sgqlc.types.Field(sgqlc.types.non_null('NetworkRecording'), graphql_name='recording')
    quota = sgqlc.types.Field('Quota', graphql_name='quota')


class CreateNetworkSeriesRecordingPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('recordings', 'quota')
    recordings = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('NetworkRecording')), graphql_name='recordings')
    quota = sgqlc.types.Field('Quota', graphql_name='quota')


class CreatePersonalChannelListPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('channel_list',)
    channel_list = sgqlc.types.Field(sgqlc.types.non_null('ChannelList'), graphql_name='channelList')


class CreateProfilePincodePayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('profile',)
    profile = sgqlc.types.Field(sgqlc.types.non_null('Profile'), graphql_name='profile')


class DeleteDevicePayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('household',)
    household = sgqlc.types.Field(sgqlc.types.non_null('Household'), graphql_name='household')


class DeleteEpisodesOfNetworkSeriesRecordingPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('events', 'quota')
    events = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('Event')), graphql_name='events')
    quota = sgqlc.types.Field('Quota', graphql_name='quota')


class DeleteEventBookmarkPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('event',)
    event = sgqlc.types.Field(sgqlc.types.non_null('Event'), graphql_name='event')


class DeleteProfilePincodePayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('profile',)
    profile = sgqlc.types.Field(sgqlc.types.non_null('Profile'), graphql_name='profile')


class DeleteRecordingBookmarkPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('recording',)
    recording = sgqlc.types.Field(sgqlc.types.non_null('Recording'), graphql_name='recording')


class DeleteRecordingPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('quota', 'event', 'recordings')
    quota = sgqlc.types.Field('Quota', graphql_name='quota')
    event = sgqlc.types.Field('Event', graphql_name='event')
    recordings = sgqlc.types.Field(sgqlc.types.list_of('Recording'), graphql_name='recordings')


class DeleteVODBookmarkPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('vod_asset',)
    vod_asset = sgqlc.types.Field(sgqlc.types.non_null('VODAsset'), graphql_name='vodAsset')


class Edge(sgqlc.types.Interface):
    __schema__ = a1_schema
    __field_names__ = ('cursor', 'location_indicator')
    cursor = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='cursor')
    location_indicator = sgqlc.types.Field(Int, graphql_name='locationIndicator')


class FavouriteItemPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('item',)
    item = sgqlc.types.Field(sgqlc.types.non_null('FavouritableItem'), graphql_name='item')


class GraphQLHeartbeat(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('interval',)
    interval = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='interval')


class HttpHeartbeat(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('url', 'interval', 'include_auth_headers')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')
    interval = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='interval')
    include_auth_headers = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='includeAuthHeaders')


class KeepSessionAlivePayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('session_timeout',)
    session_timeout = sgqlc.types.Field(Int, graphql_name='sessionTimeout')


class Nexx4Mutations(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('notify_device_activation', 'change_household_onboarding_info', 'change_profile_onboarding_info', 'change_master_pincode', 'change_household_preferences', 'change_household_community', 'create_profile_pincode', 'change_profile_pincode', 'delete_profile_pincode', 'change_profile_preferences', 'reset_profile_preferences', 'change_profile_permissions', 'play_channel', 'restart_event', 'catchup_event', 'pause_live_channel', 'play_ppvevent', 'play_recording', 'play_vodasset', 'play_trailer', 'stop_playback', 'send_playback_heartbeat', 'create_device', 'delete_device', 'change_language', 'change_device_name', 'change_device_enablement_policy', 'change_device_preview_mode', 'change_device_drmnetwork_device_id', 'create_personal_channel_list', 'set_channel_list_channels', 'change_channel_list_name', 'move_channel_list', 'delete_channel_list', 'create_channel_list', 'add_channel', 'remove_channel', 'change_initial_channel_list', 'block_channel', 'unblock_channel', 'change_channel_preferences', 'set_household_confirmed_replay_permissions', 'set_event_bookmark', 'delete_event_bookmark', 'favourite_item', 'unfavourite_item', 'set_reminder', 'change_reminder', 'cancel_reminder', 'create_network_recording', 'change_network_recording', 'delete_recording', 'create_network_series_recording', 'cancel_season_of_network_series_recording', 'cancel_network_series_recording', 'delete_episodes_of_network_series_recording', 'purchase_channel_product', 'purchase_upsell_product', 'purchase_vodproduct', 'start_vodtransaction', 'complete_vodtransaction', 'cancel_vodtransaction', 'start_and_complete_ppvtransaction', 'set_recording_bookmark', 'delete_recording_bookmark', 'set_vodbookmark', 'delete_vodbookmark', 'keep_session_alive', 'logout')
    notify_device_activation = sgqlc.types.Field(sgqlc.types.non_null('NotifyDeviceActivationPayload'), graphql_name='notifyDeviceActivation')
    change_household_onboarding_info = sgqlc.types.Field(sgqlc.types.non_null(ChangeHouseholdOnboardingInfoPayload), graphql_name='changeHouseholdOnboardingInfo', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ChangeHouseholdOnboardingInfoInput), graphql_name='input', default=None)),
))
    )
    change_profile_onboarding_info = sgqlc.types.Field(sgqlc.types.non_null(ChangeProfileOnboardingInfoPayload), graphql_name='changeProfileOnboardingInfo', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ChangeProfileOnboardingInfoInput), graphql_name='input', default=None)),
))
    )
    change_master_pincode = sgqlc.types.Field(sgqlc.types.non_null(ChangeMasterPincodePayload), graphql_name='changeMasterPincode', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ChangeMasterPincodeInput), graphql_name='input', default=None)),
))
    )
    change_household_preferences = sgqlc.types.Field(sgqlc.types.non_null(ChangeHouseholdPreferencesPayload), graphql_name='changeHouseholdPreferences', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ChangeHouseholdPreferencesInput), graphql_name='input', default=None)),
))
    )
    change_household_community = sgqlc.types.Field(sgqlc.types.non_null(ChangeHouseholdCommunityPayload), graphql_name='changeHouseholdCommunity', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ChangeHouseholdCommunityInput), graphql_name='input', default=None)),
))
    )
    create_profile_pincode = sgqlc.types.Field(sgqlc.types.non_null(CreateProfilePincodePayload), graphql_name='createProfilePincode', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CreateProfilePincodeInput), graphql_name='input', default=None)),
))
    )
    change_profile_pincode = sgqlc.types.Field(sgqlc.types.non_null(ChangeProfilePincodePayload), graphql_name='changeProfilePincode', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ChangeProfilePincodeInput), graphql_name='input', default=None)),
))
    )
    delete_profile_pincode = sgqlc.types.Field(sgqlc.types.non_null(DeleteProfilePincodePayload), graphql_name='deleteProfilePincode', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DeleteProfilePincodeInput), graphql_name='input', default=None)),
))
    )
    change_profile_preferences = sgqlc.types.Field(sgqlc.types.non_null(ChangeProfilePreferencesPayload), graphql_name='changeProfilePreferences', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ChangeProfilePreferencesInput), graphql_name='input', default=None)),
))
    )
    reset_profile_preferences = sgqlc.types.Field(sgqlc.types.non_null('ResetProfilePreferencesPayload'), graphql_name='resetProfilePreferences', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ResetProfilePreferencesInput), graphql_name='input', default=None)),
))
    )
    change_profile_permissions = sgqlc.types.Field(sgqlc.types.non_null(ChangeProfilePermissionsPayload), graphql_name='changeProfilePermissions', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ChangeProfilePermissionsInput), graphql_name='input', default=None)),
))
    )
    play_channel = sgqlc.types.Field(sgqlc.types.non_null('PlayChannelPayload'), graphql_name='playChannel', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(PlayChannelInput), graphql_name='input', default=None)),
))
    )
    restart_event = sgqlc.types.Field(sgqlc.types.non_null('RestartEventPayload'), graphql_name='restartEvent', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(RestartEventInput), graphql_name='input', default=None)),
))
    )
    catchup_event = sgqlc.types.Field(sgqlc.types.non_null(CatchupEventPayload), graphql_name='catchupEvent', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CatchupEventInput), graphql_name='input', default=None)),
))
    )
    pause_live_channel = sgqlc.types.Field(sgqlc.types.non_null('PauseLiveChannelPayload'), graphql_name='pauseLiveChannel', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(PauseLiveChannelInput), graphql_name='input', default=None)),
))
    )
    play_ppvevent = sgqlc.types.Field(sgqlc.types.non_null('PlayPPVEventPayload'), graphql_name='playPPVEvent', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(PlayPPVEventInput), graphql_name='input', default=None)),
))
    )
    play_recording = sgqlc.types.Field(sgqlc.types.non_null('PlayRecordingPayload'), graphql_name='playRecording', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(PlayRecordingInput), graphql_name='input', default=None)),
))
    )
    play_vodasset = sgqlc.types.Field(sgqlc.types.non_null('PlayVODAssetPayload'), graphql_name='playVODAsset', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(PlayVODAssetInput), graphql_name='input', default=None)),
))
    )
    play_trailer = sgqlc.types.Field(sgqlc.types.non_null('PlayTrailerPayload'), graphql_name='playTrailer', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(PlayTrailerInput), graphql_name='input', default=None)),
))
    )
    stop_playback = sgqlc.types.Field(sgqlc.types.non_null('StopPlaybackPayload'), graphql_name='stopPlayback', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(StopPlaybackInput), graphql_name='input', default=None)),
))
    )
    send_playback_heartbeat = sgqlc.types.Field(sgqlc.types.non_null('SendPlaybackHeartbeatPayload'), graphql_name='sendPlaybackHeartbeat', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(SendPlaybackHeartbeatInput), graphql_name='input', default=None)),
))
    )
    create_device = sgqlc.types.Field(sgqlc.types.non_null(CreateDevicePayload), graphql_name='createDevice', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CreateDeviceInput), graphql_name='input', default=None)),
))
    )
    delete_device = sgqlc.types.Field(sgqlc.types.non_null(DeleteDevicePayload), graphql_name='deleteDevice', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DeleteDeviceInput), graphql_name='input', default=None)),
))
    )
    change_language = sgqlc.types.Field(sgqlc.types.non_null(ChangeLanguagePayload), graphql_name='changeLanguage', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ChangeLanguageInput), graphql_name='input', default=None)),
))
    )
    change_device_name = sgqlc.types.Field(sgqlc.types.non_null(ChangeDeviceNamePayload), graphql_name='changeDeviceName', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ChangeDeviceNameInput), graphql_name='input', default=None)),
))
    )
    change_device_enablement_policy = sgqlc.types.Field(sgqlc.types.non_null(ChangeDeviceEnablementPolicyPayload), graphql_name='changeDeviceEnablementPolicy', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ChangeDeviceEnablementPolicyInput), graphql_name='input', default=None)),
))
    )
    change_device_preview_mode = sgqlc.types.Field(sgqlc.types.non_null(ChangeDevicePreviewModePayload), graphql_name='changeDevicePreviewMode', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ChangeDevicePreviewModeInput), graphql_name='input', default=None)),
))
    )
    change_device_drmnetwork_device_id = sgqlc.types.Field(sgqlc.types.non_null(ChangeDeviceDRMNetworkDeviceIdPayload), graphql_name='changeDeviceDRMNetworkDeviceId', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ChangeDeviceDRMNetworkDeviceIdInput), graphql_name='input', default=None)),
))
    )
    create_personal_channel_list = sgqlc.types.Field(sgqlc.types.non_null(CreatePersonalChannelListPayload), graphql_name='createPersonalChannelList', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CreatePersonalChannelListInput), graphql_name='input', default=None)),
))
    )
    set_channel_list_channels = sgqlc.types.Field(sgqlc.types.non_null('SetChannelListChannelsPayload'), graphql_name='setChannelListChannels', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(SetChannelListChannelsInput), graphql_name='input', default=None)),
))
    )
    change_channel_list_name = sgqlc.types.Field(sgqlc.types.non_null(ChangeChannelListNamePayload), graphql_name='changeChannelListName', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ChangeChannelListNameInput), graphql_name='input', default=None)),
))
    )
    move_channel_list = sgqlc.types.Field(sgqlc.types.non_null('ChannelListCatalog'), graphql_name='moveChannelList', args=sgqlc.types.ArgDict((
        ('channel_list_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='channelListId', default=None)),
        ('position', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='position', default=None)),
))
    )
    delete_channel_list = sgqlc.types.Field(sgqlc.types.non_null('ChannelListCatalog'), graphql_name='deleteChannelList', args=sgqlc.types.ArgDict((
        ('channel_list_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='channelListId', default=None)),
))
    )
    create_channel_list = sgqlc.types.Field(sgqlc.types.non_null('ChannelList'), graphql_name='createChannelList', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
        ('name', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='name', default=None)),
))
    )
    add_channel = sgqlc.types.Field(sgqlc.types.non_null('ChannelList'), graphql_name='addChannel', args=sgqlc.types.ArgDict((
        ('channel_list_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='channelListId', default=None)),
        ('channel_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='channelId', default=None)),
        ('position', sgqlc.types.Arg(Int, graphql_name='position', default=None)),
))
    )
    remove_channel = sgqlc.types.Field(sgqlc.types.non_null('ChannelList'), graphql_name='removeChannel', args=sgqlc.types.ArgDict((
        ('channel_list_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='channelListId', default=None)),
        ('channel_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='channelId', default=None)),
))
    )
    change_initial_channel_list = sgqlc.types.Field(sgqlc.types.non_null(ChangeInitialChannelListPayload), graphql_name='changeInitialChannelList', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ChangeInitialChannelListInput), graphql_name='input', default=None)),
))
    )
    block_channel = sgqlc.types.Field(sgqlc.types.non_null('Channel'), graphql_name='blockChannel', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
        ('channel_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='channelId', default=None)),
))
    )
    unblock_channel = sgqlc.types.Field(sgqlc.types.non_null('Channel'), graphql_name='unblockChannel', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
        ('channel_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='channelId', default=None)),
))
    )
    change_channel_preferences = sgqlc.types.Field(sgqlc.types.non_null(ChangeChannelPreferencesPayload), graphql_name='changeChannelPreferences', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ChangeChannelPreferencesInput), graphql_name='input', default=None)),
))
    )
    set_household_confirmed_replay_permissions = sgqlc.types.Field(sgqlc.types.non_null('SetHouseholdConfirmedReplayPermissionsPayload'), graphql_name='setHouseholdConfirmedReplayPermissions', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(SetHouseholdConfirmedReplayPermissionsInput), graphql_name='input', default=None)),
))
    )
    set_event_bookmark = sgqlc.types.Field(sgqlc.types.non_null('SetEventBookmarkPayload'), graphql_name='setEventBookmark', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(SetEventBookmarkInput), graphql_name='input', default=None)),
))
    )
    delete_event_bookmark = sgqlc.types.Field(sgqlc.types.non_null(DeleteEventBookmarkPayload), graphql_name='deleteEventBookmark', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DeleteEventBookmarkInput), graphql_name='input', default=None)),
))
    )
    favourite_item = sgqlc.types.Field(sgqlc.types.non_null(FavouriteItemPayload), graphql_name='favouriteItem', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(FavouriteItemInput), graphql_name='input', default=None)),
))
    )
    unfavourite_item = sgqlc.types.Field(sgqlc.types.non_null('UnfavouriteItemPayload'), graphql_name='unfavouriteItem', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(UnfavouriteItemInput), graphql_name='input', default=None)),
))
    )
    set_reminder = sgqlc.types.Field(sgqlc.types.non_null('Reminder'), graphql_name='setReminder', args=sgqlc.types.ArgDict((
        ('event_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='eventId', default=None)),
        ('before_time', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='beforeTime', default=None)),
))
    )
    change_reminder = sgqlc.types.Field(sgqlc.types.non_null('Reminder'), graphql_name='changeReminder', args=sgqlc.types.ArgDict((
        ('event_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='eventId', default=None)),
        ('before_time', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='beforeTime', default=None)),
))
    )
    cancel_reminder = sgqlc.types.Field(sgqlc.types.non_null('Event'), graphql_name='cancelReminder', args=sgqlc.types.ArgDict((
        ('event_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='eventId', default=None)),
))
    )
    create_network_recording = sgqlc.types.Field(sgqlc.types.non_null(CreateNetworkRecordingPayload), graphql_name='createNetworkRecording', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CreateNetworkRecordingInput), graphql_name='input', default=None)),
))
    )
    change_network_recording = sgqlc.types.Field(sgqlc.types.non_null(ChangeNetworkRecordingPayload), graphql_name='changeNetworkRecording', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(ChangeNetworkRecordingInput), graphql_name='input', default=None)),
))
    )
    delete_recording = sgqlc.types.Field(sgqlc.types.non_null(DeleteRecordingPayload), graphql_name='deleteRecording', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DeleteRecordingInput), graphql_name='input', default=None)),
))
    )
    create_network_series_recording = sgqlc.types.Field(sgqlc.types.non_null(CreateNetworkSeriesRecordingPayload), graphql_name='createNetworkSeriesRecording', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CreateNetworkSeriesRecordingInput), graphql_name='input', default=None)),
))
    )
    cancel_season_of_network_series_recording = sgqlc.types.Field(sgqlc.types.non_null(CancelSeasonOfNetworkSeriesRecordingPayload), graphql_name='cancelSeasonOfNetworkSeriesRecording', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CancelSeasonOfNetworkSeriesRecordingInput), graphql_name='input', default=None)),
))
    )
    cancel_network_series_recording = sgqlc.types.Field(sgqlc.types.non_null(CancelNetworkSeriesRecordingPayload), graphql_name='cancelNetworkSeriesRecording', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CancelNetworkSeriesRecordingInput), graphql_name='input', default=None)),
))
    )
    delete_episodes_of_network_series_recording = sgqlc.types.Field(sgqlc.types.non_null(DeleteEpisodesOfNetworkSeriesRecordingPayload), graphql_name='deleteEpisodesOfNetworkSeriesRecording', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DeleteEpisodesOfNetworkSeriesRecordingInput), graphql_name='input', default=None)),
))
    )
    purchase_channel_product = sgqlc.types.Field(sgqlc.types.non_null('PurchaseChannelProductPayload'), graphql_name='purchaseChannelProduct', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(PurchaseChannelProductInput), graphql_name='input', default=None)),
))
    )
    purchase_upsell_product = sgqlc.types.Field(sgqlc.types.non_null('PurchaseUpsellProductPayload'), graphql_name='purchaseUpsellProduct', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(PurchaseUpsellProductInput), graphql_name='input', default=None)),
))
    )
    purchase_vodproduct = sgqlc.types.Field(sgqlc.types.non_null('PurchaseVODProductPayload'), graphql_name='purchaseVODProduct', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(PurchaseVODProductInput), graphql_name='input', default=None)),
))
    )
    start_vodtransaction = sgqlc.types.Field(sgqlc.types.non_null('StartVODTransactionPayload'), graphql_name='startVODTransaction', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(StartVODTransactionInput), graphql_name='input', default=None)),
))
    )
    complete_vodtransaction = sgqlc.types.Field(sgqlc.types.non_null(CompleteVODTransactionPayload), graphql_name='completeVODTransaction', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CompleteVODTransactionInput), graphql_name='input', default=None)),
))
    )
    cancel_vodtransaction = sgqlc.types.Field(sgqlc.types.non_null(CancelVODTransactionPayload), graphql_name='cancelVODTransaction', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(CancelVODTransactionInput), graphql_name='input', default=None)),
))
    )
    start_and_complete_ppvtransaction = sgqlc.types.Field(sgqlc.types.non_null('StartAndCompletePPVTransactionPayload'), graphql_name='startAndCompletePPVTransaction', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(StartAndCompletePPVTransactionInput), graphql_name='input', default=None)),
))
    )
    set_recording_bookmark = sgqlc.types.Field(sgqlc.types.non_null('SetRecordingBookmarkPayload'), graphql_name='setRecordingBookmark', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(SetRecordingBookmarkInput), graphql_name='input', default=None)),
))
    )
    delete_recording_bookmark = sgqlc.types.Field(sgqlc.types.non_null(DeleteRecordingBookmarkPayload), graphql_name='deleteRecordingBookmark', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DeleteRecordingBookmarkInput), graphql_name='input', default=None)),
))
    )
    set_vodbookmark = sgqlc.types.Field(sgqlc.types.non_null('SetVODBookmarkPayload'), graphql_name='setVODBookmark', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(SetVODBookmarkInput), graphql_name='input', default=None)),
))
    )
    delete_vodbookmark = sgqlc.types.Field(sgqlc.types.non_null(DeleteVODBookmarkPayload), graphql_name='deleteVODBookmark', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(DeleteVODBookmarkInput), graphql_name='input', default=None)),
))
    )
    keep_session_alive = sgqlc.types.Field(sgqlc.types.non_null(KeepSessionAlivePayload), graphql_name='keepSessionAlive')
    logout = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='logout')


class Nexx4Queries(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('me', 'languages', 'available_communities', 'available_parental_ratings', 'household', 'check_pincode', 'initial_channel_list', 'channel_lists', 'channel_list', 'channel', 'channels', 'recommended_replay_channels', 'event', 'series', 'channel_products', 'channel_product', 'upsell_products', 'product_bundle', 'subscriptions_rows', 'environment', 'recordings', 'recording', 'recording_quota', 'reminders', 'reminder', 'my_library', 'my_library_header', 'play_channel', 'restart_event', 'catchup_event', 'pause_live_event', 'play_recording', 'genres', 'search_genres', 'recommendation_rows', 'recommendation_grid', 'home_rows', 'home_header', 'search_rows', 'vod_root_content_folder_list', 'content_folder_list', 'content_folder', 'vod_folder', 'vod_asset', 'vod_product', 'vod_series', 'vod_products', 'resource_bundles', 'search_keywords', 'trending_searches', 'search', 'version_info', 'messages')
    me = sgqlc.types.Field('User', graphql_name='me')
    languages = sgqlc.types.Field('LanguageCatalog', graphql_name='languages')
    available_communities = sgqlc.types.Field('CommunityCatalog', graphql_name='availableCommunities')
    available_parental_ratings = sgqlc.types.Field('ParentalRatingCatalog', graphql_name='availableParentalRatings')
    household = sgqlc.types.Field('Household', graphql_name='household')
    check_pincode = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='checkPincode', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
        ('pincode', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='pincode', default=None)),
        ('pincode_kinds', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(PincodeKind)), graphql_name='pincodeKinds', default=None)),
))
    )
    initial_channel_list = sgqlc.types.Field('ChannelList', graphql_name='initialChannelList', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
))
    )
    channel_lists = sgqlc.types.Field('ChannelListCatalog', graphql_name='channelLists', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
        ('kind_filter', sgqlc.types.Arg(sgqlc.types.list_of(ChannelListKind), graphql_name='kindFilter', default=None)),
))
    )
    channel_list = sgqlc.types.Field('ChannelList', graphql_name='channelList', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    channel = sgqlc.types.Field('Channel', graphql_name='channel', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    channels = sgqlc.types.Field('ChannelsConnection', graphql_name='channels', args=sgqlc.types.ArgDict((
        ('pagination', sgqlc.types.Arg(sgqlc.types.non_null(FullPaginationParams), graphql_name='pagination', default=None)),
        ('filter', sgqlc.types.Arg(ChannelFilterParams, graphql_name='filter', default=None)),
        ('sorting', sgqlc.types.Arg(ChannelSortingParams, graphql_name='sorting', default=None)),
))
    )
    recommended_replay_channels = sgqlc.types.Field('ChannelsConnection', graphql_name='recommendedReplayChannels')
    event = sgqlc.types.Field('Event', graphql_name='event', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    series = sgqlc.types.Field('Series', graphql_name='series', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    channel_products = sgqlc.types.Field('ChannelProductCatalog', graphql_name='channelProducts', args=sgqlc.types.ArgDict((
        ('channel_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='channelId', default=None)),
))
    )
    channel_product = sgqlc.types.Field('ChannelProduct', graphql_name='channelProduct', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    upsell_products = sgqlc.types.Field('ProductCatalog', graphql_name='upsellProducts', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
        ('kind', sgqlc.types.Arg(sgqlc.types.non_null(UpsellProductsContextKind), graphql_name='kind', default=None)),
        ('object_id', sgqlc.types.Arg(ID, graphql_name='objectId', default=None)),
))
    )
    product_bundle = sgqlc.types.Field('ProductBundle', graphql_name='productBundle', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    subscriptions_rows = sgqlc.types.Field('ContentFolderList', graphql_name='subscriptionsRows', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
))
    )
    environment = sgqlc.types.Field('Environment', graphql_name='environment')
    recordings = sgqlc.types.Field('RecordingsConnection', graphql_name='recordings', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
        ('pagination', sgqlc.types.Arg(sgqlc.types.non_null(FullPaginationParams), graphql_name='pagination', default=None)),
        ('filter', sgqlc.types.Arg(RecordingsFilterParams, graphql_name='filter', default=None)),
))
    )
    recording = sgqlc.types.Field('Recording', graphql_name='recording', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    recording_quota = sgqlc.types.Field('Quota', graphql_name='recordingQuota')
    reminders = sgqlc.types.Field('ReminderCatalog', graphql_name='reminders', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
        ('start_date', sgqlc.types.Arg(Date, graphql_name='startDate', default=None)),
        ('end_date', sgqlc.types.Arg(Date, graphql_name='endDate', default=None)),
))
    )
    reminder = sgqlc.types.Field('Reminder', graphql_name='reminder', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    my_library = sgqlc.types.Field('ContentFolderList', graphql_name='myLibrary', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
        ('only_display_adult_content', sgqlc.types.Arg(sgqlc.types.non_null(Boolean), graphql_name='onlyDisplayAdultContent', default=None)),
))
    )
    my_library_header = sgqlc.types.Field('ContentFolder', graphql_name='myLibraryHeader', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
        ('only_display_adult_content', sgqlc.types.Arg(sgqlc.types.non_null(Boolean), graphql_name='onlyDisplayAdultContent', default=None)),
))
    )
    play_channel = sgqlc.types.Field('ChannelPlaybackInfo', graphql_name='playChannel', args=sgqlc.types.ArgDict((
        ('channel_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='channelId', default=None)),
))
    )
    restart_event = sgqlc.types.Field('EventPlaybackInfo', graphql_name='restartEvent', args=sgqlc.types.ArgDict((
        ('event_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='eventId', default=None)),
))
    )
    catchup_event = sgqlc.types.Field('EventPlaybackInfo', graphql_name='catchupEvent', args=sgqlc.types.ArgDict((
        ('event_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='eventId', default=None)),
))
    )
    pause_live_event = sgqlc.types.Field('EventPlaybackInfo', graphql_name='pauseLiveEvent', args=sgqlc.types.ArgDict((
        ('event_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='eventId', default=None)),
))
    )
    play_recording = sgqlc.types.Field('RecordingPlaybackInfo', graphql_name='playRecording', args=sgqlc.types.ArgDict((
        ('recording_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='recordingId', default=None)),
))
    )
    genres = sgqlc.types.Field('GenreCatalog', graphql_name='genres')
    search_genres = sgqlc.types.Field('GenreCatalog', graphql_name='searchGenres')
    recommendation_rows = sgqlc.types.Field('RecommendationListCatalog', graphql_name='recommendationRows', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
        ('page', sgqlc.types.Arg(sgqlc.types.non_null(PageWithRecommendations), graphql_name='page', default=None)),
        ('item_id', sgqlc.types.Arg(ID, graphql_name='itemId', default=None)),
))
    )
    recommendation_grid = sgqlc.types.Field('RecommendationGrid', graphql_name='recommendationGrid', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
))
    )
    home_rows = sgqlc.types.Field('ContentFolderList', graphql_name='homeRows', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
))
    )
    home_header = sgqlc.types.Field('ContentFolder', graphql_name='homeHeader', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
))
    )
    search_rows = sgqlc.types.Field('ContentFolderList', graphql_name='searchRows', args=sgqlc.types.ArgDict((
        ('context', sgqlc.types.Arg(sgqlc.types.non_null(SearchContext), graphql_name='context', default=None)),
))
    )
    vod_root_content_folder_list = sgqlc.types.Field('ContentFolderList', graphql_name='vodRootContentFolderList', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
))
    )
    content_folder_list = sgqlc.types.Field('ContentFolderList', graphql_name='contentFolderList', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    content_folder = sgqlc.types.Field('ContentFolder', graphql_name='contentFolder', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    vod_folder = sgqlc.types.Field('VODFolder', graphql_name='vodFolder', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    vod_asset = sgqlc.types.Field('VODAsset', graphql_name='vodAsset', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    vod_product = sgqlc.types.Field('VODProduct', graphql_name='vodProduct', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    vod_series = sgqlc.types.Field('VODSeries', graphql_name='vodSeries', args=sgqlc.types.ArgDict((
        ('id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='id', default=None)),
))
    )
    vod_products = sgqlc.types.Field('VODProductCatalog', graphql_name='vodProducts', args=sgqlc.types.ArgDict((
        ('asset_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='assetId', default=None)),
))
    )
    resource_bundles = sgqlc.types.Field('ResourceBundlesPayload', graphql_name='resourceBundles', args=sgqlc.types.ArgDict((
        ('app_version', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='appVersion', default=None)),
))
    )
    search_keywords = sgqlc.types.Field('KeywordCatalog', graphql_name='searchKeywords', args=sgqlc.types.ArgDict((
        ('input', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='input', default=None)),
        ('filter', sgqlc.types.Arg(sgqlc.types.non_null(SearchFilter), graphql_name='filter', default=None)),
))
    )
    trending_searches = sgqlc.types.Field('StringCatalog', graphql_name='trendingSearches')
    search = sgqlc.types.Field('ContentFolderList', graphql_name='search', args=sgqlc.types.ArgDict((
        ('keyword', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='keyword', default=None)),
        ('context', sgqlc.types.Arg(sgqlc.types.non_null(SearchContext), graphql_name='context', default=None)),
        ('filter', sgqlc.types.Arg(sgqlc.types.non_null(SearchFilter), graphql_name='filter', default=None)),
))
    )
    version_info = sgqlc.types.Field('VersionInfo', graphql_name='versionInfo')
    messages = sgqlc.types.Field(sgqlc.types.non_null('MessagesConnection'), graphql_name='messages', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
        ('pagination', sgqlc.types.Arg(sgqlc.types.non_null(FullPaginationParams), graphql_name='pagination', default=None)),
        ('filter', sgqlc.types.Arg(sgqlc.types.non_null(MessageFilterParams), graphql_name='filter', default=None)),
))
    )


class NotifyDeviceActivationPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('success',)
    success = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='success')


class PageInfo(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('has_next_page', 'has_previous_page', 'start_cursor', 'end_cursor')
    has_next_page = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasNextPage')
    has_previous_page = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasPreviousPage')
    start_cursor = sgqlc.types.Field(String, graphql_name='startCursor')
    end_cursor = sgqlc.types.Field(String, graphql_name='endCursor')


class PauseLiveChannelPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('playback_info',)
    playback_info = sgqlc.types.Field(sgqlc.types.non_null('TimeshiftPlaybackInfo'), graphql_name='playbackInfo')


class PlayChannelPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('playback_info',)
    playback_info = sgqlc.types.Field(sgqlc.types.non_null('ChannelPlaybackInfo'), graphql_name='playbackInfo')


class PlayPPVEventPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('playback_info',)
    playback_info = sgqlc.types.Field(sgqlc.types.non_null('ChannelPlaybackInfo'), graphql_name='playbackInfo')


class PlayRecordingPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('playback_info',)
    playback_info = sgqlc.types.Field(sgqlc.types.non_null('RecordingPlaybackInfo'), graphql_name='playbackInfo')


class PlayTrailerPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('playback_info',)
    playback_info = sgqlc.types.Field(sgqlc.types.non_null('TrailerPlaybackInfo'), graphql_name='playbackInfo')


class PlayVODAssetPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('playback_info',)
    playback_info = sgqlc.types.Field(sgqlc.types.non_null('VODPlaybackInfo'), graphql_name='playbackInfo')


class PlaybackInfo(sgqlc.types.Interface):
    __schema__ = a1_schema
    __field_names__ = ('delivery_kind', 'url', 'session_id', 'heartbeat', 'playback_restrictions', 'rtsp_headers')
    delivery_kind = sgqlc.types.Field(sgqlc.types.non_null(ContentDeliveryKind), graphql_name='deliveryKind')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')
    session_id = sgqlc.types.Field(ID, graphql_name='sessionId')
    heartbeat = sgqlc.types.Field('Heartbeat', graphql_name='heartbeat')
    playback_restrictions = sgqlc.types.Field(sgqlc.types.list_of('PlaybackRestriction'), graphql_name='playbackRestrictions')
    rtsp_headers = sgqlc.types.Field('RtspHeaders', graphql_name='rtspHeaders')


class PlaybackRestriction(sgqlc.types.Interface):
    __schema__ = a1_schema
    __field_names__ = ('message',)
    message = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='message')


class Product(sgqlc.types.Interface):
    __schema__ = a1_schema
    __field_names__ = ('title', 'kind', 'short_description', 'full_description', 'price', 'thumbnail', 'background_image', 'trailers', 'related_content', 'entitlement', 'purchase_info', 'selfcare_url')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    kind = sgqlc.types.Field(sgqlc.types.non_null(ProductKind), graphql_name='kind')
    short_description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='shortDescription', args=sgqlc.types.ArgDict((
        ('max_length', sgqlc.types.Arg(Int, graphql_name='maxLength', default=None)),
))
    )
    full_description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='fullDescription')
    price = sgqlc.types.Field('Price', graphql_name='price')
    thumbnail = sgqlc.types.Field('Image', graphql_name='thumbnail', args=sgqlc.types.ArgDict((
        ('height', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='height', default=None)),
))
    )
    background_image = sgqlc.types.Field('Image', graphql_name='backgroundImage', args=sgqlc.types.ArgDict((
        ('width', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='width', default=None)),
        ('height', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='height', default=None)),
))
    )
    trailers = sgqlc.types.Field(sgqlc.types.non_null('TrailerCatalog'), graphql_name='trailers')
    related_content = sgqlc.types.Field('ContentFolderList', graphql_name='relatedContent')
    entitlement = sgqlc.types.Field('ProductEntitlement', graphql_name='entitlement')
    purchase_info = sgqlc.types.Field('ProductPurchaseInfo', graphql_name='purchaseInfo')
    selfcare_url = sgqlc.types.Field(String, graphql_name='selfcareUrl')


class PurchaseChannelProductPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('channel_product',)
    channel_product = sgqlc.types.Field(sgqlc.types.non_null('ChannelProduct'), graphql_name='channelProduct')


class PurchaseUpsellProductPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('product',)
    product = sgqlc.types.Field(sgqlc.types.non_null(Product), graphql_name='product')


class PurchaseVODProductPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('product',)
    product = sgqlc.types.Field(sgqlc.types.non_null('VODProduct'), graphql_name='product')


class Recording(sgqlc.types.Interface):
    __schema__ = a1_schema
    __field_names__ = ('start', 'end', 'status', 'size', 'delete_protected', 'personal_info', 'channel', 'channel_name')
    start = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name='start')
    end = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name='end')
    status = sgqlc.types.Field(sgqlc.types.non_null(RecordingStatus), graphql_name='status')
    size = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='size')
    delete_protected = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='deleteProtected')
    personal_info = sgqlc.types.Field(sgqlc.types.non_null('PersonalRecordingInfo'), graphql_name='personalInfo', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
))
    )
    channel = sgqlc.types.Field('Channel', graphql_name='channel')
    channel_name = sgqlc.types.Field(String, graphql_name='channelName')


class ResetProfilePreferencesPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('profile', 'full_channel_list')
    profile = sgqlc.types.Field(sgqlc.types.non_null('Profile'), graphql_name='profile')
    full_channel_list = sgqlc.types.Field(sgqlc.types.non_null('ChannelList'), graphql_name='fullChannelList')


class ResourceBundlesPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('application', 'configuration', 'localization', 'skin', 'remotecontrol')
    application = sgqlc.types.Field('ResourceBundle', graphql_name='application')
    configuration = sgqlc.types.Field('ResourceBundle', graphql_name='configuration')
    localization = sgqlc.types.Field('ResourceBundle', graphql_name='localization')
    skin = sgqlc.types.Field('ResourceBundle', graphql_name='skin')
    remotecontrol = sgqlc.types.Field('ResourceBundle', graphql_name='remotecontrol')


class RestartEventPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('playback_info',)
    playback_info = sgqlc.types.Field(sgqlc.types.non_null('TimeshiftPlaybackInfo'), graphql_name='playbackInfo')


class RtspHeaders(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('transport', 'session')
    transport = sgqlc.types.Field(String, graphql_name='transport')
    session = sgqlc.types.Field(String, graphql_name='session')


class SeasonInfo(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('number', 'cursor', 'episode_count')
    number = sgqlc.types.Field(Int, graphql_name='number')
    cursor = sgqlc.types.Field(String, graphql_name='cursor')
    episode_count = sgqlc.types.Field(Int, graphql_name='episodeCount')


class SendPlaybackHeartbeatPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('session_id', 'interval')
    session_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='sessionId')
    interval = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='interval')


class SetChannelListChannelsPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('channel_list',)
    channel_list = sgqlc.types.Field(sgqlc.types.non_null('ChannelList'), graphql_name='channelList')


class SetEventBookmarkPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('event',)
    event = sgqlc.types.Field(sgqlc.types.non_null('Event'), graphql_name='event')


class SetHouseholdConfirmedReplayPermissionsPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('success',)
    success = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='success')


class SetRecordingBookmarkPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('recording',)
    recording = sgqlc.types.Field(sgqlc.types.non_null(Recording), graphql_name='recording')


class SetVODBookmarkPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('vod_asset',)
    vod_asset = sgqlc.types.Field(sgqlc.types.non_null('VODAsset'), graphql_name='vodAsset')


class StartAndCompletePPVTransactionPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('event',)
    event = sgqlc.types.Field(sgqlc.types.non_null('Event'), graphql_name='event')


class StartVODTransactionPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('entitlement',)
    entitlement = sgqlc.types.Field(sgqlc.types.non_null('VODAssetEntitlement'), graphql_name='entitlement')


class StopPlaybackPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('success',)
    success = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='success')


class UnfavouriteItemPayload(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('item',)
    item = sgqlc.types.Field(sgqlc.types.non_null('FavouritableItem'), graphql_name='item')


class VersionInfo(sgqlc.types.Type):
    __schema__ = a1_schema
    __field_names__ = ('description',)
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')


class Bookmark(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('position', 'audio', 'subtitle')
    position = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='position')
    audio = sgqlc.types.Field(String, graphql_name='audio')
    subtitle = sgqlc.types.Field(String, graphql_name='subtitle')


class Channel(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('title', 'description', 'kind', 'parental_rating', 'default_number', 'logo', 'background_image', 'before_time', 'after_time', 'events', 'events_at', 'event_blocks', 'user_info', 'personal_info', 'entitlements', 'dvb_info', 'hybrid_display_behaviour', 'hybrid_playback_behaviour', 'fallback_info', 'related_content')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    description = sgqlc.types.Field(String, graphql_name='description')
    kind = sgqlc.types.Field(sgqlc.types.non_null(ChannelKind), graphql_name='kind')
    parental_rating = sgqlc.types.Field(sgqlc.types.non_null('ParentalRating'), graphql_name='parentalRating')
    default_number = sgqlc.types.Field(Int, graphql_name='defaultNumber')
    logo = sgqlc.types.Field('Image', graphql_name='logo', args=sgqlc.types.ArgDict((
        ('width', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='width', default=None)),
        ('height', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='height', default=None)),
        ('flavour', sgqlc.types.Arg(ImageFlavour, graphql_name='flavour', default=None)),
))
    )
    background_image = sgqlc.types.Field('Image', graphql_name='backgroundImage', args=sgqlc.types.ArgDict((
        ('width', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='width', default=None)),
        ('height', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='height', default=None)),
))
    )
    before_time = sgqlc.types.Field(Int, graphql_name='beforeTime')
    after_time = sgqlc.types.Field(Int, graphql_name='afterTime')
    events = sgqlc.types.Field('EventCatalog', graphql_name='events', args=sgqlc.types.ArgDict((
        ('start', sgqlc.types.Arg(sgqlc.types.non_null(Date), graphql_name='start', default=None)),
        ('duration', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='duration', default=None)),
))
    )
    events_at = sgqlc.types.Field('EventCatalog', graphql_name='eventsAt', args=sgqlc.types.ArgDict((
        ('time', sgqlc.types.Arg(sgqlc.types.non_null(Date), graphql_name='time', default=None)),
        ('previous', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='previous', default=None)),
        ('following', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='following', default=None)),
))
    )
    event_blocks = sgqlc.types.Field(sgqlc.types.list_of('EventCatalog'), graphql_name='eventBlocks', args=sgqlc.types.ArgDict((
        ('start', sgqlc.types.Arg(sgqlc.types.non_null(Date), graphql_name='start', default=None)),
        ('block_durations', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(Int)), graphql_name='blockDurations', default=None)),
))
    )
    user_info = sgqlc.types.Field('UserChannelInfo', graphql_name='userInfo')
    personal_info = sgqlc.types.Field('PersonalChannelInfo', graphql_name='personalInfo', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
))
    )
    entitlements = sgqlc.types.Field('ChannelEntitlements', graphql_name='entitlements')
    dvb_info = sgqlc.types.Field('DvbInfo', graphql_name='dvbInfo')
    hybrid_display_behaviour = sgqlc.types.Field(sgqlc.types.non_null(HybridChannelDisplayBehaviour), graphql_name='hybridDisplayBehaviour')
    hybrid_playback_behaviour = sgqlc.types.Field(sgqlc.types.non_null(HybridChannelPlaybackBehaviour), graphql_name='hybridPlaybackBehaviour')
    fallback_info = sgqlc.types.Field('ChannelPlaybackInfo', graphql_name='fallbackInfo')
    related_content = sgqlc.types.Field('ContentFolderList', graphql_name='relatedContent')


class ChannelEntitlements(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('live_tv', 'pause_live_tv', 'restart_tv', 'catchup_tv', 'network_recording', 'local_recording', 'household_confirmed_replay_permissions')
    live_tv = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='liveTV')
    pause_live_tv = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='pauseLiveTV')
    restart_tv = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='restartTV')
    catchup_tv = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='catchupTV')
    network_recording = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='networkRecording')
    local_recording = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='localRecording')
    household_confirmed_replay_permissions = sgqlc.types.Field(Boolean, graphql_name='householdConfirmedReplayPermissions')


class ChannelList(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('name', 'kind', 'channels', 'active_channel')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    kind = sgqlc.types.Field(sgqlc.types.non_null(ChannelListKind), graphql_name='kind')
    channels = sgqlc.types.Field(sgqlc.types.non_null('ChannelListChannelsConnection'), graphql_name='channels', args=sgqlc.types.ArgDict((
        ('first', sgqlc.types.Arg(Int, graphql_name='first', default=None)),
        ('after', sgqlc.types.Arg(String, graphql_name='after', default=None)),
        ('last', sgqlc.types.Arg(Int, graphql_name='last', default=None)),
        ('before', sgqlc.types.Arg(String, graphql_name='before', default=None)),
))
    )
    active_channel = sgqlc.types.Field(Channel, graphql_name='activeChannel', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
))
    )


class ChannelListCatalog(sgqlc.types.Type, Cacheable, Catalog):
    __schema__ = a1_schema
    __field_names__ = ('items',)
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(ChannelList)), graphql_name='items')


class ChannelListChannelsConnection(sgqlc.types.relay.Connection, Cacheable, Connection):
    __schema__ = a1_schema
    __field_names__ = ('edges',)
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('ChannelListChannelsEdge')), graphql_name='edges')


class ChannelListChannelsEdge(sgqlc.types.Type, Cacheable, Edge):
    __schema__ = a1_schema
    __field_names__ = ('node', 'channel_list_number')
    node = sgqlc.types.Field(sgqlc.types.non_null(Channel), graphql_name='node')
    channel_list_number = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='channelListNumber')


class ChannelPlaybackInfo(sgqlc.types.Type, Cacheable, PlaybackInfo):
    __schema__ = a1_schema
    __field_names__ = ('channel',)
    channel = sgqlc.types.Field(sgqlc.types.non_null(Channel), graphql_name='channel')


class ChannelProduct(sgqlc.types.Type, Cacheable, Product):
    __schema__ = a1_schema
    __field_names__ = ('subtitle', 'description', 'channels')
    subtitle = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='subtitle')
    description = sgqlc.types.Field(String, graphql_name='description')
    channels = sgqlc.types.Field(sgqlc.types.non_null('ChannelProductChannelsConnection'), graphql_name='channels', args=sgqlc.types.ArgDict((
        ('first', sgqlc.types.Arg(Int, graphql_name='first', default=None)),
        ('after', sgqlc.types.Arg(String, graphql_name='after', default=None)),
        ('last', sgqlc.types.Arg(Int, graphql_name='last', default=None)),
        ('before', sgqlc.types.Arg(String, graphql_name='before', default=None)),
))
    )


class ChannelProductCatalog(sgqlc.types.Type, Cacheable, Catalog):
    __schema__ = a1_schema
    __field_names__ = ('items',)
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(ChannelProduct)), graphql_name='items')


class ChannelProductChannelsConnection(sgqlc.types.relay.Connection, Cacheable, Connection):
    __schema__ = a1_schema
    __field_names__ = ('edges',)
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('ChannelProductChannelsEdge')), graphql_name='edges')


class ChannelProductChannelsEdge(sgqlc.types.Type, Cacheable, Edge):
    __schema__ = a1_schema
    __field_names__ = ('node',)
    node = sgqlc.types.Field(sgqlc.types.non_null(Channel), graphql_name='node')


class ChannelsConnection(sgqlc.types.relay.Connection, Cacheable, Connection):
    __schema__ = a1_schema
    __field_names__ = ('edges',)
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('ChannelsEdge')), graphql_name='edges')


class ChannelsEdge(sgqlc.types.Type, Cacheable, Edge):
    __schema__ = a1_schema
    __field_names__ = ('node',)
    node = sgqlc.types.Field(sgqlc.types.non_null(Channel), graphql_name='node')


class Community(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('title', 'description')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    description = sgqlc.types.Field(String, graphql_name='description')


class CommunityCatalog(sgqlc.types.Type, Cacheable, Catalog):
    __schema__ = a1_schema
    __field_names__ = ('items',)
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Community)), graphql_name='items')


class ContentFolder(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('kind', 'items', 'title', 'refresh_at')
    kind = sgqlc.types.Field(sgqlc.types.non_null(ContentFolderKind), graphql_name='kind')
    items = sgqlc.types.Field('ContentFolderContentItemsConnection', graphql_name='items', args=sgqlc.types.ArgDict((
        ('first', sgqlc.types.Arg(Int, graphql_name='first', default=None)),
        ('after', sgqlc.types.Arg(String, graphql_name='after', default=None)),
        ('last', sgqlc.types.Arg(Int, graphql_name='last', default=None)),
        ('before', sgqlc.types.Arg(String, graphql_name='before', default=None)),
        ('include_cursor', sgqlc.types.Arg(Boolean, graphql_name='includeCursor', default=None)),
))
    )
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    refresh_at = sgqlc.types.Field(Date, graphql_name='refreshAt')


class ContentFolderContentItemsConnection(sgqlc.types.relay.Connection, Cacheable, Connection):
    __schema__ = a1_schema
    __field_names__ = ('edges',)
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('ContentFolderContentItemsEdge')), graphql_name='edges')


class ContentFolderContentItemsEdge(sgqlc.types.Type, Cacheable, Edge):
    __schema__ = a1_schema
    __field_names__ = ('node',)
    node = sgqlc.types.Field(sgqlc.types.non_null('ContentItem'), graphql_name='node')


class ContentFolderList(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('folders',)
    folders = sgqlc.types.Field(sgqlc.types.non_null('ContentFolderListContentFoldersConnection'), graphql_name='folders', args=sgqlc.types.ArgDict((
        ('first', sgqlc.types.Arg(Int, graphql_name='first', default=None)),
        ('after', sgqlc.types.Arg(String, graphql_name='after', default=None)),
        ('last', sgqlc.types.Arg(Int, graphql_name='last', default=None)),
        ('before', sgqlc.types.Arg(String, graphql_name='before', default=None)),
))
    )


class ContentFolderListContentFoldersConnection(sgqlc.types.relay.Connection, Cacheable, Connection):
    __schema__ = a1_schema
    __field_names__ = ('edges',)
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('ContentFolderListContentFoldersEdge')), graphql_name='edges')


class ContentFolderListContentFoldersEdge(sgqlc.types.Type, Cacheable, Edge):
    __schema__ = a1_schema
    __field_names__ = ('node',)
    node = sgqlc.types.Field(sgqlc.types.non_null(ContentFolder), graphql_name='node')


class DVBScanParameters(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('frequency', 'modulation', 'symbol_rate')
    frequency = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='frequency')
    modulation = sgqlc.types.Field(sgqlc.types.non_null(DVBModulationKind), graphql_name='modulation')
    symbol_rate = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='symbolRate')


class Device(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('client_generated_id', 'device_type', 'language', 'name', 'renameable', 'registration_time', 'removable', 'fingerprint_id', 'removable_from', 'device_enablement_policies', 'preview_mode_enabled', 'event_logging_options', 'quick_guide_video', 'drm_network_device_id')
    client_generated_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='clientGeneratedId')
    device_type = sgqlc.types.Field(sgqlc.types.non_null(DeviceType), graphql_name='deviceType')
    language = sgqlc.types.Field(sgqlc.types.non_null('Language'), graphql_name='language')
    name = sgqlc.types.Field(String, graphql_name='name')
    renameable = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='renameable')
    registration_time = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name='registrationTime')
    removable = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='removable')
    fingerprint_id = sgqlc.types.Field(String, graphql_name='fingerprintId')
    removable_from = sgqlc.types.Field(Date, graphql_name='removableFrom')
    device_enablement_policies = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('DeviceEnablementPolicy')), graphql_name='deviceEnablementPolicies')
    preview_mode_enabled = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='previewModeEnabled')
    event_logging_options = sgqlc.types.Field(sgqlc.types.list_of(EventLoggingOption), graphql_name='eventLoggingOptions')
    quick_guide_video = sgqlc.types.Field('VODAsset', graphql_name='quickGuideVideo')
    drm_network_device_id = sgqlc.types.Field(String, graphql_name='drmNetworkDeviceId')


class DeviceCatalog(sgqlc.types.Type, Cacheable, Catalog):
    __schema__ = a1_schema
    __field_names__ = ('items',)
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Device)), graphql_name='items')


class DeviceEnablementPolicy(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('title', 'short_title', 'enabled', 'enabled_until')
    title = sgqlc.types.Field(String, graphql_name='title')
    short_title = sgqlc.types.Field(String, graphql_name='shortTitle')
    enabled = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='enabled')
    enabled_until = sgqlc.types.Field(Date, graphql_name='enabledUntil')


class DvbInfo(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('onid', 'tsid', 'sid')
    onid = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='onid')
    tsid = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='tsid')
    sid = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='sid')


class Environment(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('scan_parameters',)
    scan_parameters = sgqlc.types.Field(DVBScanParameters, graphql_name='scanParameters')


class EpisodeInfo(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('number', 'title', 'season')
    number = sgqlc.types.Field(Int, graphql_name='number')
    title = sgqlc.types.Field(String, graphql_name='title')
    season = sgqlc.types.Field(Int, graphql_name='season')


class Event(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('title', 'start', 'end', 'event_id', 'parental_rating', 'channel', 'blackout', 'ppv', 'small_image', 'thumbnail', 'background_image', 'metadata', 'entitlements', 'start_over_tvbefore_time', 'start_over_tvafter_time', 'start_over_playback_start_position', 'start_over_playback_continue_position', 'start_over_playback_stop_position', 'personal_info', 'related_content')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    start = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name='start')
    end = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name='end')
    event_id = sgqlc.types.Field(ID, graphql_name='eventId')
    parental_rating = sgqlc.types.Field(sgqlc.types.non_null('ParentalRating'), graphql_name='parentalRating')
    channel = sgqlc.types.Field(Channel, graphql_name='channel')
    blackout = sgqlc.types.Field(Boolean, graphql_name='blackout')
    ppv = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='ppv')
    small_image = sgqlc.types.Field('Image', graphql_name='smallImage', args=sgqlc.types.ArgDict((
        ('width', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='width', default=None)),
        ('height', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='height', default=None)),
))
    )
    thumbnail = sgqlc.types.Field('Image', graphql_name='thumbnail', args=sgqlc.types.ArgDict((
        ('height', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='height', default=None)),
))
    )
    background_image = sgqlc.types.Field('Image', graphql_name='backgroundImage', args=sgqlc.types.ArgDict((
        ('width', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='width', default=None)),
        ('height', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='height', default=None)),
))
    )
    metadata = sgqlc.types.Field(sgqlc.types.non_null('Metadata'), graphql_name='metadata')
    entitlements = sgqlc.types.Field('EventEntitlements', graphql_name='entitlements')
    start_over_tvbefore_time = sgqlc.types.Field(Int, graphql_name='startOverTVBeforeTime')
    start_over_tvafter_time = sgqlc.types.Field(Int, graphql_name='startOverTVAfterTime')
    start_over_playback_start_position = sgqlc.types.Field(Int, graphql_name='startOverPlaybackStartPosition')
    start_over_playback_continue_position = sgqlc.types.Field(Int, graphql_name='startOverPlaybackContinuePosition')
    start_over_playback_stop_position = sgqlc.types.Field(Int, graphql_name='startOverPlaybackStopPosition')
    personal_info = sgqlc.types.Field('PersonalEventInfo', graphql_name='personalInfo', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
))
    )
    related_content = sgqlc.types.Field(ContentFolderList, graphql_name='relatedContent')


class EventCatalog(sgqlc.types.Type, Cacheable, Catalog):
    __schema__ = a1_schema
    __field_names__ = ('items',)
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Event)), graphql_name='items')


class EventConcurrencyPlaybackRestriction(sgqlc.types.Type, PlaybackRestriction):
    __schema__ = a1_schema
    __field_names__ = ()


class EventEntitlements(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('live_tv', 'ppv_tv', 'pause_live_tv', 'restart_tv', 'catchup_tv', 'catchup_tvavailable_until', 'network_recording', 'network_recording_plannable_until', 'needs_concurrency_token')
    live_tv = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='liveTV')
    ppv_tv = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='ppvTV')
    pause_live_tv = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='pauseLiveTV')
    restart_tv = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='restartTV')
    catchup_tv = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='catchupTV')
    catchup_tvavailable_until = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name='catchupTVAvailableUntil')
    network_recording = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='networkRecording')
    network_recording_plannable_until = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name='networkRecordingPlannableUntil')
    needs_concurrency_token = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='needsConcurrencyToken')


class EventPlaybackInfo(sgqlc.types.Type, PlaybackInfo):
    __schema__ = a1_schema
    __field_names__ = ('event',)
    event = sgqlc.types.Field(sgqlc.types.non_null(Event), graphql_name='event')


class Genre(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('title',)
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')


class GenreCatalog(sgqlc.types.Type, Cacheable, Catalog):
    __schema__ = a1_schema
    __field_names__ = ('items',)
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Genre)), graphql_name='items')


class GroupingInfo(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('title', 'start_cursor', 'end_cursor', 'episode_count', 'select_behaviour')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    start_cursor = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='startCursor')
    end_cursor = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='endCursor')
    episode_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='episodeCount')
    select_behaviour = sgqlc.types.Field(sgqlc.types.non_null(GroupInfoSelectBehaviour), graphql_name='selectBehaviour')


class Household(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('profiles', 'devices', 'max_number_of_unmanaged_devices', 'max_number_of_confirmed_replay_channels', 'community', 'master_pincode', 'display_non_adult_content', 'track_viewing_behaviour', 'agreed_to_terms_and_conditions', 'onboarding_info', 'preview_mode_allowed', 'can_move_operator_channel_lists')
    profiles = sgqlc.types.Field(sgqlc.types.non_null('ProfileCatalog'), graphql_name='profiles')
    devices = sgqlc.types.Field(sgqlc.types.non_null(DeviceCatalog), graphql_name='devices')
    max_number_of_unmanaged_devices = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='maxNumberOfUnmanagedDevices')
    max_number_of_confirmed_replay_channels = sgqlc.types.Field(Int, graphql_name='maxNumberOfConfirmedReplayChannels')
    community = sgqlc.types.Field(Community, graphql_name='community')
    master_pincode = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='masterPincode')
    display_non_adult_content = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='displayNonAdultContent')
    track_viewing_behaviour = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='trackViewingBehaviour')
    agreed_to_terms_and_conditions = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='agreedToTermsAndConditions')
    onboarding_info = sgqlc.types.Field(sgqlc.types.non_null('HouseholdOnboardingInfo'), graphql_name='onboardingInfo')
    preview_mode_allowed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='previewModeAllowed')
    can_move_operator_channel_lists = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canMoveOperatorChannelLists')


class HouseholdOnboardingInfo(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('master_pincode_step_completed', 'community_step_completed', 'privacy_step_completed', 'replay_step_completed')
    master_pincode_step_completed = sgqlc.types.Field(Date, graphql_name='masterPincodeStepCompleted')
    community_step_completed = sgqlc.types.Field(Date, graphql_name='communityStepCompleted')
    privacy_step_completed = sgqlc.types.Field(Date, graphql_name='privacyStepCompleted')
    replay_step_completed = sgqlc.types.Field(Date, graphql_name='replayStepCompleted')


class Image(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('url', 'width', 'height')
    url = sgqlc.types.Field(String, graphql_name='url')
    width = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='width')
    height = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='height')


class JailbrokenPlaybackRestriction(sgqlc.types.Type, PlaybackRestriction):
    __schema__ = a1_schema
    __field_names__ = ()


class KeywordCatalog(sgqlc.types.Type, Cacheable, Catalog):
    __schema__ = a1_schema
    __field_names__ = ('items',)
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='items')


class Language(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('title', 'code')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    code = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='code')


class LanguageCatalog(sgqlc.types.Type, Cacheable, Catalog):
    __schema__ = a1_schema
    __field_names__ = ('items',)
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Language)), graphql_name='items')


class Message(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('title', 'message', 'icon', 'label', 'display_kind', 'status', 'timestamp', 'valid_from', 'valid_until')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    message = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='message')
    icon = sgqlc.types.Field(Image, graphql_name='icon', args=sgqlc.types.ArgDict((
        ('width', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='width', default=None)),
        ('height', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='height', default=None)),
        ('flavour', sgqlc.types.Arg(ImageFlavour, graphql_name='flavour', default=None)),
))
    )
    label = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='label')
    display_kind = sgqlc.types.Field(sgqlc.types.non_null(MessageDisplayKind), graphql_name='displayKind')
    status = sgqlc.types.Field(sgqlc.types.non_null(MessageStatus), graphql_name='status')
    timestamp = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name='timestamp')
    valid_from = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name='validFrom')
    valid_until = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name='validUntil')


class MessagesConnection(sgqlc.types.relay.Connection, Cacheable, Connection):
    __schema__ = a1_schema
    __field_names__ = ('edges',)
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('MessagesEdge')), graphql_name='edges')


class MessagesEdge(sgqlc.types.Type, Cacheable, Edge):
    __schema__ = a1_schema
    __field_names__ = ('node',)
    node = sgqlc.types.Field(sgqlc.types.non_null(Message), graphql_name='node')


class Metadata(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('title', 'original_title', 'short_description', 'full_description', 'genre', 'series_info', 'episode_info', 'actors', 'directors', 'country', 'year', 'ratings')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    original_title = sgqlc.types.Field(String, graphql_name='originalTitle')
    short_description = sgqlc.types.Field(String, graphql_name='shortDescription', args=sgqlc.types.ArgDict((
        ('max_length', sgqlc.types.Arg(Int, graphql_name='maxLength', default=None)),
))
    )
    full_description = sgqlc.types.Field(String, graphql_name='fullDescription')
    genre = sgqlc.types.Field(Genre, graphql_name='genre')
    series_info = sgqlc.types.Field('SeriesInfo', graphql_name='seriesInfo')
    episode_info = sgqlc.types.Field(EpisodeInfo, graphql_name='episodeInfo')
    actors = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='actors')
    directors = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='directors')
    country = sgqlc.types.Field(String, graphql_name='country')
    year = sgqlc.types.Field(Int, graphql_name='year')
    ratings = sgqlc.types.Field(sgqlc.types.list_of('Rating'), graphql_name='ratings')


class NetworkRecording(sgqlc.types.Type, Recording, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('allow_playback', 'available_until', 'event', 'before_time_events', 'after_time_events', 'related_content')
    allow_playback = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='allowPlayback')
    available_until = sgqlc.types.Field(Date, graphql_name='availableUntil')
    event = sgqlc.types.Field(sgqlc.types.non_null(Event), graphql_name='event')
    before_time_events = sgqlc.types.Field(sgqlc.types.list_of(Event), graphql_name='beforeTimeEvents')
    after_time_events = sgqlc.types.Field(sgqlc.types.list_of(Event), graphql_name='afterTimeEvents')
    related_content = sgqlc.types.Field(ContentFolderList, graphql_name='relatedContent')


class OutputPlaybackRestriction(sgqlc.types.Type, PlaybackRestriction):
    __schema__ = a1_schema
    __field_names__ = ()


class PPVProduct(sgqlc.types.Type, Cacheable, Product):
    __schema__ = a1_schema
    __field_names__ = ()


class ParentalRating(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('title', 'description', 'icon', 'rank', 'adult')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')
    icon = sgqlc.types.Field(Image, graphql_name='icon', args=sgqlc.types.ArgDict((
        ('width', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='width', default=None)),
        ('height', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='height', default=None)),
        ('flavour', sgqlc.types.Arg(ImageFlavour, graphql_name='flavour', default=None)),
))
    )
    rank = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='rank')
    adult = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='adult')


class ParentalRatingCatalog(sgqlc.types.Type, Cacheable, Catalog):
    __schema__ = a1_schema
    __field_names__ = ('items',)
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(ParentalRating)), graphql_name='items')


class PersonalChannelInfo(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('blocked', 'audio_language', 'subtitle_language')
    blocked = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='blocked')
    audio_language = sgqlc.types.Field(String, graphql_name='audioLanguage')
    subtitle_language = sgqlc.types.Field(String, graphql_name='subtitleLanguage')


class PersonalEventInfo(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('reminder_set', 'favourited', 'bookmark', 'recordings', 'rating')
    reminder_set = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='reminderSet')
    favourited = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='favourited')
    bookmark = sgqlc.types.Field(Bookmark, graphql_name='bookmark')
    recordings = sgqlc.types.Field(sgqlc.types.list_of(Recording), graphql_name='recordings', args=sgqlc.types.ArgDict((
        ('kind_filter', sgqlc.types.Arg(RecordingKind, graphql_name='kindFilter', default=None)),
))
    )
    rating = sgqlc.types.Field('Rating', graphql_name='rating')


class PersonalProductInfo(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('favourited',)
    favourited = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='favourited')


class PersonalRecordingInfo(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('favourited', 'bookmark', 'part_of_series_recording', 'season_cancelled', 'series_cancelled')
    favourited = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='favourited')
    bookmark = sgqlc.types.Field(Bookmark, graphql_name='bookmark')
    part_of_series_recording = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='partOfSeriesRecording')
    season_cancelled = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='seasonCancelled')
    series_cancelled = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='seriesCancelled')


class PersonalVODInfo(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('favourited', 'bookmark')
    favourited = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='favourited')
    bookmark = sgqlc.types.Field(Bookmark, graphql_name='bookmark')


class Price(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('amount', 'currency')
    amount = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='amount')
    currency = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='currency')


class ProductBundle(sgqlc.types.Type, Cacheable, Product):
    __schema__ = a1_schema
    __field_names__ = ('products',)
    products = sgqlc.types.Field(sgqlc.types.non_null('ProductCatalog'), graphql_name='products')


class ProductCatalog(sgqlc.types.Type, Cacheable, Catalog):
    __schema__ = a1_schema
    __field_names__ = ('items',)
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Product)), graphql_name='items')


class ProductEntitlement(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('available_until',)
    available_until = sgqlc.types.Field(Date, graphql_name='availableUntil')


class ProductPurchaseInfo(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('status',)
    status = sgqlc.types.Field(sgqlc.types.non_null(ProductPurchaseStatus), graphql_name='status')


class Profile(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('name', 'kind', 'protection', 'pincode', 'preferences', 'permissions', 'onboarding_info')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')
    kind = sgqlc.types.Field(sgqlc.types.non_null(ProfileKind), graphql_name='kind')
    protection = sgqlc.types.Field(ProfileProtection, graphql_name='protection')
    pincode = sgqlc.types.Field(String, graphql_name='pincode')
    preferences = sgqlc.types.Field(sgqlc.types.non_null('ProfilePreferences'), graphql_name='preferences')
    permissions = sgqlc.types.Field(sgqlc.types.non_null('ProfilePermissions'), graphql_name='permissions')
    onboarding_info = sgqlc.types.Field(sgqlc.types.non_null('ProfileOnboardingInfo'), graphql_name='onboardingInfo')


class ProfileCatalog(sgqlc.types.Type, Cacheable, Catalog):
    __schema__ = a1_schema
    __field_names__ = ('items',)
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Profile)), graphql_name='items')


class ProfileOnboardingInfo(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('age_rating_step_completed',)
    age_rating_step_completed = sgqlc.types.Field(Date, graphql_name='ageRatingStepCompleted')


class ProfilePermissions(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('parental_rating', 'mask_content', 'can_purchase', 'purchase_protection', 'purchase_limit', 'display_blocked_channels', 'other_profiles_content', 'edit_my_library', 'create_recordings', 'logout_pincode', 'edit_channel_lists', 'single_channel_list', 'access_search', 'resort_apps', 'manage_apps')
    parental_rating = sgqlc.types.Field(sgqlc.types.non_null(ParentalRating), graphql_name='parentalRating')
    mask_content = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='maskContent')
    can_purchase = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='canPurchase')
    purchase_protection = sgqlc.types.Field(sgqlc.types.non_null(ProfileProtection), graphql_name='purchaseProtection')
    purchase_limit = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='purchaseLimit')
    display_blocked_channels = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='displayBlockedChannels')
    other_profiles_content = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='otherProfilesContent')
    edit_my_library = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='editMyLibrary')
    create_recordings = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='createRecordings')
    logout_pincode = sgqlc.types.Field(String, graphql_name='logoutPincode')
    edit_channel_lists = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='editChannelLists')
    single_channel_list = sgqlc.types.Field(ChannelList, graphql_name='singleChannelList')
    access_search = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='accessSearch')
    resort_apps = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='resortApps')
    manage_apps = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='manageApps')


class ProfilePreferences(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('app_sorting', 'display_not_subscribed_channels', 'first_audio_language', 'second_audio_language', 'first_subtitle_language', 'second_subtitle_language', 'hard_of_hearing', 'visually_impaired', 'avatar')
    app_sorting = sgqlc.types.Field(sgqlc.types.non_null(AppSorting), graphql_name='appSorting')
    display_not_subscribed_channels = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='displayNotSubscribedChannels')
    first_audio_language = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='firstAudioLanguage')
    second_audio_language = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='secondAudioLanguage')
    first_subtitle_language = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='firstSubtitleLanguage')
    second_subtitle_language = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='secondSubtitleLanguage')
    hard_of_hearing = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hardOfHearing')
    visually_impaired = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='visuallyImpaired')
    avatar = sgqlc.types.Field(Image, graphql_name='avatar', args=sgqlc.types.ArgDict((
        ('width', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='width', default=None)),
        ('height', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='height', default=None)),
))
    )


class Quota(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('allowed', 'used', 'kind')
    allowed = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='allowed')
    used = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='used')
    kind = sgqlc.types.Field(QuotaKind, graphql_name='kind')


class Rating(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('value', 'name')
    value = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='value')
    name = sgqlc.types.Field(String, graphql_name='name')


class RecommendationGrid(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('title', 'items')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('RecommendationGridItem')), graphql_name='items')


class RecommendationGridItem(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('title', 'width', 'height', 'content')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    width = sgqlc.types.Field(Int, graphql_name='width')
    height = sgqlc.types.Field(Int, graphql_name='height')
    content = sgqlc.types.Field(sgqlc.types.non_null('Recommendation'), graphql_name='content')


class RecommendationList(sgqlc.types.Type, Cacheable, Catalog):
    __schema__ = a1_schema
    __field_names__ = ('items', 'title')
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('Recommendation')), graphql_name='items')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')


class RecommendationListCatalog(sgqlc.types.Type, Cacheable, Catalog):
    __schema__ = a1_schema
    __field_names__ = ('items',)
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(RecommendationList)), graphql_name='items')


class RecordingPlaybackInfo(sgqlc.types.Type, PlaybackInfo):
    __schema__ = a1_schema
    __field_names__ = ('recording', 'end_of_episode_offset')
    recording = sgqlc.types.Field(sgqlc.types.non_null(Recording), graphql_name='recording')
    end_of_episode_offset = sgqlc.types.Field(Int, graphql_name='endOfEpisodeOffset')


class RecordingsConnection(sgqlc.types.relay.Connection, Cacheable, Connection):
    __schema__ = a1_schema
    __field_names__ = ('edges',)
    edges = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('RecordingsEdge')), graphql_name='edges')


class RecordingsEdge(sgqlc.types.Type, Cacheable, Edge):
    __schema__ = a1_schema
    __field_names__ = ('node',)
    node = sgqlc.types.Field(sgqlc.types.non_null('ListedRecording'), graphql_name='node')


class Reminder(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('before_time', 'event')
    before_time = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='beforeTime')
    event = sgqlc.types.Field(sgqlc.types.non_null(Event), graphql_name='event')


class ReminderCatalog(sgqlc.types.Type, Cacheable, Catalog):
    __schema__ = a1_schema
    __field_names__ = ('items',)
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Reminder)), graphql_name='items')


class ResourceBundle(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('url', 'version')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')
    version = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='version')


class Series(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('title', 'subtitle', 'channel', 'thumbnail', 'background_image', 'parental_rating', 'episode_count', 'season_infos', 'grouping_infos', 'content', 'edge_for_active_episode', 'active_episode')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    subtitle = sgqlc.types.Field(String, graphql_name='subtitle')
    channel = sgqlc.types.Field(Channel, graphql_name='channel')
    thumbnail = sgqlc.types.Field(Image, graphql_name='thumbnail', args=sgqlc.types.ArgDict((
        ('height', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='height', default=None)),
))
    )
    background_image = sgqlc.types.Field(Image, graphql_name='backgroundImage', args=sgqlc.types.ArgDict((
        ('width', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='width', default=None)),
        ('height', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='height', default=None)),
))
    )
    parental_rating = sgqlc.types.Field(sgqlc.types.non_null(ParentalRating), graphql_name='parentalRating')
    episode_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='episodeCount')
    season_infos = sgqlc.types.Field(sgqlc.types.list_of(SeasonInfo), graphql_name='seasonInfos')
    grouping_infos = sgqlc.types.Field(sgqlc.types.list_of(GroupingInfo), graphql_name='groupingInfos')
    content = sgqlc.types.Field(sgqlc.types.non_null(ContentFolder), graphql_name='content')
    edge_for_active_episode = sgqlc.types.Field(sgqlc.types.non_null(ContentFolderContentItemsEdge), graphql_name='edgeForActiveEpisode', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
))
    )
    active_episode = sgqlc.types.Field(sgqlc.types.non_null(ActiveEpisodeInfo), graphql_name='activeEpisode', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
))
    )


class SeriesInfo(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('title',)
    title = sgqlc.types.Field(String, graphql_name='title')


class StringCatalog(sgqlc.types.Type, Cacheable, Catalog):
    __schema__ = a1_schema
    __field_names__ = ('items',)
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='items')


class TimeshiftPlaybackInfo(sgqlc.types.Type, PlaybackInfo):
    __schema__ = a1_schema
    __field_names__ = ('event', 'stream_start', 'stream_end', 'maximum_buffer_size', 'end_of_stream_behaviour')
    event = sgqlc.types.Field(sgqlc.types.non_null(Event), graphql_name='event')
    stream_start = sgqlc.types.Field(Date, graphql_name='streamStart')
    stream_end = sgqlc.types.Field(Date, graphql_name='streamEnd')
    maximum_buffer_size = sgqlc.types.Field(Int, graphql_name='maximumBufferSize')
    end_of_stream_behaviour = sgqlc.types.Field(sgqlc.types.non_null(EndOfStreamBehaviour), graphql_name='endOfStreamBehaviour')


class Trailer(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('title', 'linked_item')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    linked_item = sgqlc.types.Field(sgqlc.types.non_null('TrailerContentItem'), graphql_name='linkedItem')


class TrailerCatalog(sgqlc.types.Type, Cacheable, Catalog):
    __schema__ = a1_schema
    __field_names__ = ('items',)
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Trailer)), graphql_name='items')


class TrailerPlaybackInfo(sgqlc.types.Type, PlaybackInfo):
    __schema__ = a1_schema
    __field_names__ = ('trailer',)
    trailer = sgqlc.types.Field(sgqlc.types.non_null(Trailer), graphql_name='trailer')


class User(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('household', 'device', 'first_name', 'guest_mode')
    household = sgqlc.types.Field(sgqlc.types.non_null(Household), graphql_name='household')
    device = sgqlc.types.Field(sgqlc.types.non_null(Device), graphql_name='device')
    first_name = sgqlc.types.Field(String, graphql_name='firstName')
    guest_mode = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='guestMode')


class UserChannelInfo(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('subscribed',)
    subscribed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='subscribed')


class VODAsset(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('title', 'thumbnail', 'background_image', 'duration', 'parental_rating', 'trailers', 'metadata', 'entitlements', 'personal_info', 'related_content')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    thumbnail = sgqlc.types.Field(Image, graphql_name='thumbnail', args=sgqlc.types.ArgDict((
        ('height', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='height', default=None)),
))
    )
    background_image = sgqlc.types.Field(Image, graphql_name='backgroundImage', args=sgqlc.types.ArgDict((
        ('width', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='width', default=None)),
        ('height', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='height', default=None)),
))
    )
    duration = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='duration')
    parental_rating = sgqlc.types.Field(sgqlc.types.non_null(ParentalRating), graphql_name='parentalRating')
    trailers = sgqlc.types.Field(sgqlc.types.non_null(TrailerCatalog), graphql_name='trailers')
    metadata = sgqlc.types.Field(sgqlc.types.non_null(Metadata), graphql_name='metadata')
    entitlements = sgqlc.types.Field(sgqlc.types.non_null('VODAssetEntitlementCatalog'), graphql_name='entitlements')
    personal_info = sgqlc.types.Field(PersonalVODInfo, graphql_name='personalInfo', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
))
    )
    related_content = sgqlc.types.Field(ContentFolderList, graphql_name='relatedContent')


class VODAssetEntitlement(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('playback', 'temporary', 'playback_available_until', 'product')
    playback = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='playback')
    temporary = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='temporary')
    playback_available_until = sgqlc.types.Field(Date, graphql_name='playbackAvailableUntil')
    product = sgqlc.types.Field('VODProduct', graphql_name='product')


class VODAssetEntitlementCatalog(sgqlc.types.Type, Cacheable, Catalog):
    __schema__ = a1_schema
    __field_names__ = ('items',)
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(VODAssetEntitlement)), graphql_name='items')


class VODFolder(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('title', 'thumbnail', 'background_image', 'parental_rating', 'content', 'use_parent_folder', 'parent_content_folder_list')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    thumbnail = sgqlc.types.Field(Image, graphql_name='thumbnail', args=sgqlc.types.ArgDict((
        ('height', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='height', default=None)),
))
    )
    background_image = sgqlc.types.Field(Image, graphql_name='backgroundImage', args=sgqlc.types.ArgDict((
        ('width', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='width', default=None)),
        ('height', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='height', default=None)),
))
    )
    parental_rating = sgqlc.types.Field(sgqlc.types.non_null(ParentalRating), graphql_name='parentalRating')
    content = sgqlc.types.Field(sgqlc.types.non_null(ContentFolderList), graphql_name='content')
    use_parent_folder = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='useParentFolder')
    parent_content_folder_list = sgqlc.types.Field(ContentFolderList, graphql_name='parentContentFolderList')


class VODPlaybackInfo(sgqlc.types.Type, PlaybackInfo):
    __schema__ = a1_schema
    __field_names__ = ('vod_asset', 'end_of_episode_offset')
    vod_asset = sgqlc.types.Field(sgqlc.types.non_null(VODAsset), graphql_name='vodAsset')
    end_of_episode_offset = sgqlc.types.Field(Int, graphql_name='endOfEpisodeOffset')


class VODProduct(sgqlc.types.Type, Cacheable, Product):
    __schema__ = a1_schema
    __field_names__ = ('original_title', 'parental_rating', 'genre', 'actors', 'directors', 'available_assets', 'video_quality', 'personal_info', 'package_product')
    original_title = sgqlc.types.Field(String, graphql_name='originalTitle')
    parental_rating = sgqlc.types.Field(ParentalRating, graphql_name='parentalRating')
    genre = sgqlc.types.Field(Genre, graphql_name='genre')
    actors = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='actors')
    directors = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='directors')
    available_assets = sgqlc.types.Field(ContentFolder, graphql_name='availableAssets')
    video_quality = sgqlc.types.Field(VideoQuality, graphql_name='videoQuality')
    personal_info = sgqlc.types.Field(PersonalProductInfo, graphql_name='personalInfo', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
))
    )
    package_product = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='packageProduct')


class VODProductCatalog(sgqlc.types.Type, Cacheable, Catalog):
    __schema__ = a1_schema
    __field_names__ = ('items',)
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(VODProduct)), graphql_name='items')


class VODSeries(sgqlc.types.Type, Cacheable):
    __schema__ = a1_schema
    __field_names__ = ('title', 'thumbnail', 'background_image', 'parental_rating', 'episode_count', 'season_numbers', 'season_infos', 'content', 'edge_for_season', 'edge_for_active_episode', 'related_content')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')
    thumbnail = sgqlc.types.Field(Image, graphql_name='thumbnail', args=sgqlc.types.ArgDict((
        ('height', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='height', default=None)),
))
    )
    background_image = sgqlc.types.Field(Image, graphql_name='backgroundImage', args=sgqlc.types.ArgDict((
        ('width', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='width', default=None)),
        ('height', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='height', default=None)),
))
    )
    parental_rating = sgqlc.types.Field(sgqlc.types.non_null(ParentalRating), graphql_name='parentalRating')
    episode_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='episodeCount')
    season_numbers = sgqlc.types.Field(sgqlc.types.list_of(Int), graphql_name='seasonNumbers')
    season_infos = sgqlc.types.Field(sgqlc.types.list_of(SeasonInfo), graphql_name='seasonInfos')
    content = sgqlc.types.Field(sgqlc.types.non_null(ContentFolder), graphql_name='content')
    edge_for_season = sgqlc.types.Field(sgqlc.types.non_null(ContentFolderContentItemsEdge), graphql_name='edgeForSeason', args=sgqlc.types.ArgDict((
        ('season_number', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='seasonNumber', default=None)),
))
    )
    edge_for_active_episode = sgqlc.types.Field(sgqlc.types.non_null(ContentFolderContentItemsEdge), graphql_name='edgeForActiveEpisode', args=sgqlc.types.ArgDict((
        ('profile_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='profileId', default=None)),
))
    )
    related_content = sgqlc.types.Field(ContentFolderList, graphql_name='relatedContent')


class VideoQualityPlaybackRestriction(sgqlc.types.Type, PlaybackRestriction):
    __schema__ = a1_schema
    __field_names__ = ('quality',)
    quality = sgqlc.types.Field(sgqlc.types.non_null(VideoQuality), graphql_name='quality')



########################################################################
# Unions
########################################################################
class ContentItem(sgqlc.types.Union):
    __schema__ = a1_schema
    __types__ = (Event, NetworkRecording, Series, Channel, ChannelProduct, VODFolder, VODAsset, VODProduct, VODSeries, ProductBundle)


class FavouritableItem(sgqlc.types.Union):
    __schema__ = a1_schema
    __types__ = (Event, NetworkRecording, VODAsset, VODProduct)


class Heartbeat(sgqlc.types.Union):
    __schema__ = a1_schema
    __types__ = (HttpHeartbeat, GraphQLHeartbeat)


class ListedRecording(sgqlc.types.Union):
    __schema__ = a1_schema
    __types__ = (NetworkRecording,)


class Recommendation(sgqlc.types.Union):
    __schema__ = a1_schema
    __types__ = (Event, NetworkRecording, Channel, ChannelProduct)


class TrailerContentItem(sgqlc.types.Union):
    __schema__ = a1_schema
    __types__ = (VODAsset, VODProduct)



########################################################################
# Schema Entry Points
########################################################################
a1_schema.query_type = Nexx4Queries
a1_schema.mutation_type = Nexx4Mutations
a1_schema.subscription_type = None

