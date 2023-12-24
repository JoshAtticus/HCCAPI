# HCCAPI
Cool open-source API used for unlocking Huawei Portable/USB Modems. Supports v1 (old) and v2a1 IMEIs.

## AQBAEAT (answering questions before anyone even asks them)

### Why?
I found an old Huawei Pocket WiFi 2 and made it my life goal to unlock it from Vodafone so I could use 3G Optus before it shuts down.

### Testing?
Should work on *most* Huawei modems with a v1 (starting in 86) or v2a1 (starting in 35) IMEI. Only tested on a Huawei E585.

### How legal is this?
Depends on what you do with it.

### What features does it have?
- Unlock and flash codes for v1 and v2a1 IMEIs (most IMEIs starting in 86 for v1 and 35 for v2a1)
- Cloudflared IP logging (also logs IMEIs you unlock for legal reasons)
- Use in anything (most APIs need a dumb captcha, this one is completely free with no captcha)
- IMEI validation (does this even matter)

### What if someone spams it?
All requests are logged and ratelimiting is set to only allow 3 requests per minute.

### What if someone abuses it?
Then they'll be the one getting in trouble when I provide logs to their ISP and law enforcement in their country.
