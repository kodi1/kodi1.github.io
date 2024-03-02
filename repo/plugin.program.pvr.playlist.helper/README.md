### What is this Kodi "PVR Playlist Helper" addon about? 

The addon simply does the following:
1. Automatically (on schedule) downloads M3U files from local drive or from remote URL resource and serves it locally.
2. Raplaces dynamic stream URLs with static, which helps the Kodi TV Channel's manager to remember the changes done on any channel. 
3. Allows modifications of any stream property
4. Reorder streams
5. Disable streams 
6. TODO Add and combine up to 2 other playlist 

### How to install

The addon is supported on Kodi version 19 and later. Install by manually downloading it from here or from the official Kodi repo.

### Replacing stream properties:

To modify any stream property in a playlist, you need to provide a JSON map with key-value pairs, where the key is the name of the stream.
For instance, the following map tells the app to change the group-title stream attribute of each stream:

```javascript
{
  'Channel 1': { 'group-title': 'National', 'tvg-id': 'channel.1.id' },
  'The Sport Channel': { 'group-title': 'Sports' }
}
```

As a result, a stream like this:

`#EXTINF:-1 tvg-id="id1" group-title="cinema",Channel 1`

becomes:

`#EXTINF:-1 tvg-id="channel.1.id" group-title="National",Channel 1`

### Dynamic to static URL redirection

Dynamic stream URLs are changed to static ones and servered from a small HTTP server which redirects to the original stream. 
This helps Kodi TV Manager remembers any changes you do to any stream/channels. 
As a result of the modification, stream URL like this:

`http://cdn.streaming.server.com/stream/55432A32F12CC19B`

becomes:

`http://127.0.0.1:18910/streams/Channel1` 

### Reordering streams

If enabled, the stream reorder function will order the streams as they appear in the map file. If a stream is missing from the map file it will added at the end after all mapped streams. 

### Disabling streams

To disable a stream, simple add the disabled property to the stream map:

```javascript
{
  'Channel 1': { 'disabled': true }
}
```
