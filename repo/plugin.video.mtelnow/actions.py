# -*- coding: utf-8 -*-
import sys
from common import *

headers = {'SDSEVO_USER_ID': str(user_id),
           'SDSEVO_DEVICE_ID': device_id,
           'SDSEVO_SESSION_ID': session_id,
}
client = my_gqlc(headers=headers, session=session)

if sys.argv[1] == 'favoriteItem':
    profile_id = int(sys.argv[2])
    item_id = int(sys.argv[3])
    variables = {"input": {"itemId": item_id, "profileId": profile_id, "itemKind": "EVENT"}, "profileId": profile_id}
    query = '''
mutation favouriteItem($input: FavouriteItemInput!, $profileId: ID!) {
  favouriteItem(input: $input) {
    item {
      ... on VODAsset {
        ...cacheInfoFragment
        personalVODInfo: personalInfo(profileId: $profileId) {
          ...personalVODInfoFragment
          favourited
          __typename
        }
        __typename
      }
      ... on Recording {
        ... on NetworkRecording {
          ...cacheInfoFragment
          personalRecordingInfo: personalInfo(profileId: $profileId) {
            ...personalRecordingInfoFragment
            favourited
            __typename
          }
          __typename
        }
        __typename
      }
      ... on Event {
        ...cacheInfoFragment
        personalEventInfo: personalInfo(profileId: $profileId) {
          ...personalEventInfoFragment
          favourited
          __typename
        }
        __typename
      }
      ... on VODProduct {
        ...cacheInfoFragment
        personalProductInfo: personalInfo(profileId: $profileId) {
          ...personalProductInfoFragment
          favourited
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
}

fragment cacheInfoFragment on Cacheable {
  __typename
  id
  expiry
}

fragment personalVODInfoFragment on PersonalVODInfo {
  ...cacheInfoFragment
  bookmark {
    ...bookmarkFragment
    __typename
  }
  __typename
}

fragment bookmarkFragment on Bookmark {
  ...cacheInfoFragment
  position
  audio
  subtitle
  __typename
}

fragment personalEventInfoFragment on PersonalEventInfo {
  ...cacheInfoFragment
  recordings(kindFilter: NETWORK) {
    ... on NetworkRecording {
      id
      start
      end
      status
      availableUntil
      channel {
        ...cacheInfoFragment
        title
        kind
        parentalRating {
          ...parentalRatingFragment
          __typename
        }
        __typename
      }
      personalRecordingInfo: personalInfo(profileId: $profileId) {
        ...personalRecordingInfoFragment
        __typename
      }
      __typename
    }
    __typename
  }
  bookmark {
    ...bookmarkFragment
    __typename
  }
  __typename
}

fragment personalRecordingInfoFragment on PersonalRecordingInfo {
  bookmark {
    ...cacheInfoFragment
    position
    __typename
  }
  partOfSeriesRecording
  seasonCancelled
  seriesCancelled
  __typename
}

fragment parentalRatingFragment on ParentalRating {
  ...cacheInfoFragment
  title
  description
  rank
  adult
  __typename
}

fragment personalProductInfoFragment on PersonalProductInfo {
  ...cacheInfoFragment
  favourited
  __typename
}
'''
    client.execute(query, variables=variables)
elif sys.argv[1] == 'unfavoriteItem':
    profile_id = int(sys.argv[2])
    item_id = int(sys.argv[3])
    variables = {"input": {"itemId": item_id, "profileId": profile_id, "itemKind": "EVENT"}, "profileId": profile_id}
    query = '''
mutation unfavouriteItem($input: UnfavouriteItemInput!, $profileId: ID!) {
  unfavouriteItem(input: $input) {
    item {
      ... on VODAsset {
        ...cacheInfoFragment
        personalVODInfo: personalInfo(profileId: $profileId) {
          ...personalVODInfoFragment
          favourited
          __typename
        }
        __typename
      }
      ... on Recording {
        ... on NetworkRecording {
          ...cacheInfoFragment
          personalRecordingInfo: personalInfo(profileId: $profileId) {
            ...personalRecordingInfoFragment
            favourited
            __typename
          }
          __typename
        }
        __typename
      }
      ... on Event {
        ...cacheInfoFragment
        personalEventInfo: personalInfo(profileId: $profileId) {
          ...personalEventInfoFragment
          favourited
          __typename
        }
        __typename
      }
      ... on VODProduct {
        ...cacheInfoFragment
        personalProductInfo: personalInfo(profileId: $profileId) {
          ...personalProductInfoFragment
          favourited
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
}

fragment cacheInfoFragment on Cacheable {
  __typename
  id
  expiry
}

fragment personalVODInfoFragment on PersonalVODInfo {
  ...cacheInfoFragment
  bookmark {
    ...bookmarkFragment
    __typename
  }
  __typename
}

fragment bookmarkFragment on Bookmark {
  ...cacheInfoFragment
  position
  audio
  subtitle
  __typename
}

fragment personalEventInfoFragment on PersonalEventInfo {
  ...cacheInfoFragment
  recordings(kindFilter: NETWORK) {
    ... on NetworkRecording {
      id
      start
      end
      status
      availableUntil
      channel {
        ...cacheInfoFragment
        title
        kind
        parentalRating {
          ...parentalRatingFragment
          __typename
        }
        __typename
      }
      personalRecordingInfo: personalInfo(profileId: $profileId) {
        ...personalRecordingInfoFragment
        __typename
      }
      __typename
    }
    __typename
  }
  bookmark {
    ...bookmarkFragment
    __typename
  }
  __typename
}

fragment personalRecordingInfoFragment on PersonalRecordingInfo {
  bookmark {
    ...cacheInfoFragment
    position
    __typename
  }
  partOfSeriesRecording
  seasonCancelled
  seriesCancelled
  __typename
}

fragment parentalRatingFragment on ParentalRating {
  ...cacheInfoFragment
  title
  description
  rank
  adult
  __typename
}

fragment personalProductInfoFragment on PersonalProductInfo {
  ...cacheInfoFragment
  favourited
  __typename
}
'''
    client.execute(query, variables=variables)
    xbmc.executebuiltin("Container.Refresh")
