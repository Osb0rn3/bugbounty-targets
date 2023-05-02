# Bugbounty Targets

An automated GitHub Actions-based crawler that fetches and updates public scopes from popular bug bounty platforms. This project aims to provide an up-to-date, centralized list of in-scope assets for bug bounty hunters.

## Supported Platforms

Currently, the following bug bounty platforms are supported:

- [HackerOne](https://github.com/Osb0rn3/bugbounty-targets/blob/main/programs/hackerone.json)
- [BugCrowd](https://github.com/Osb0rn3/bugbounty-targets/blob/main/programs/bugcrowd.json)
- [Intigriti](https://github.com/Osb0rn3/bugbounty-targets/blob/main/programs/intigriti.json)
- [YesWeHack](https://github.com/Osb0rn3/bugbounty-targets/blob/main/programs/yeswehack.json)

## 🚀Download Guide

<details>
<summary><b>HackerOne</b></summary>

### Get all subs
```bash
curl -s "https://raw.githubusercontent.com/Osb0rn3/bugbounty-targets/main/programs/hackerone.json" | jq -r '.[].relationships.structured_scopes.data[].attributes.asset_identifier' | grep -Eo '[a-zA-Z0-9]+([.-][a-zA-Z0-9]+)*\.[a-zA-Z]{2,}' | anew
```

### Get subs using orgname
![image](https://user-images.githubusercontent.com/72344025/234682490-3c9b4f9d-aad0-4dce-9277-5f7b7b87a0b5.png)
```bash
curl -s "https://raw.githubusercontent.com/Osb0rn3/bugbounty-targets/main/programs/hackerone.json" | jq -r '.[] | select(.attributes.name=="HackerOne") | .relationships.structured_scopes.data[].attributes.asset_identifier' | grep -Eo '[a-zA-Z0-9]+([.-][a-zA-Z0-9]+)*\.[a-zA-Z]{2,}' | anew
```
</details>

<details>
<summary><b>BugCrowd</b></summary>

### Get all subs
```bash
curl -s "https://raw.githubusercontent.com/Osb0rn3/bugbounty-targets/main/programs/bugcrowd.json" | jq -r '.[].target_groups[].targets[].name' | grep -Eo '[a-zA-Z0-9]+([.-][a-zA-Z0-9]+)*\.[a-zA-Z]{2,}' | anew
```

### Get subs using program_url in_scope and in_scope
![image](https://user-images.githubusercontent.com/72344025/234680472-6d7da018-f325-4812-aabf-9a5e414cdeef.png)
```bash
curl -s "https://raw.githubusercontent.com/Osb0rn3/bugbounty-targets/main/programs/bugcrowd.json" | jq -r '.[] | select(.program_url=="/dell-com") | .target_groups[].targets[].name' | grep -Eo '[a-zA-Z0-9]+([.-][a-zA-Z0-9]+)*\.[a-zA-Z]{2,}' | anew
```

### Get subs using program_url only in_scope
![image](https://user-images.githubusercontent.com/72344025/234680651-5ce28fa8-71e6-414f-81d0-7f5f03a33d15.png)
```bash
curl -s "https://raw.githubusercontent.com/Osb0rn3/bugbounty-targets/main/programs/bugcrowd.json" | jq -r '.[] | select(.program_url=="/dell-product") | .target_groups[] | select(.in_scope==true) | .targets[].name' | grep -Eo '[a-zA-Z0-9]+([.-][a-zA-Z0-9]+)*\.[a-zA-Z]{2,}' | anew
```

### Get only wildcard subs using program_url only in_scope
```bash
curl -s "https://raw.githubusercontent.com/Osb0rn3/bugbounty-targets/main/programs/bugcrowd.json" | jq -r '.[] | select(.program_url=="/tesla") | .target_groups[] | select(.in_scope==true) | .targets[].name' | grep "*." | anew
```
</details>

<details>
<summary><b>Intigriti</b></summary>

### Get all subs
```bash
curl -s "https://raw.githubusercontent.com/Osb0rn3/bugbounty-targets/main/programs/intigriti.json" | jq -r '.[].domains[].endpoint' | grep -Eo '[a-zA-Z0-9]+([.-][a-zA-Z0-9]+)*\.[a-zA-Z]{2,}' | anew
```

### Get subs using program handle name
![image](https://user-images.githubusercontent.com/72344025/234679727-fef11a91-c8f6-4623-b176-e92cdf5b027d.png)
```bash
curl -s "https://raw.githubusercontent.com/Osb0rn3/bugbounty-targets/main/programs/intigriti.json" | jq -r '.[] | select(.handle=="upholdcom") | .domains[].endpoint' | grep -Eo '[a-zA-Z0-9]+([.-][a-zA-Z0-9]+)*\.[a-zA-Z]{2,}' | anew
```
</details>

## Support and Questions

For any questions or support, feel free to reach out on Twitter: [@AmirMSafari](https://twitter.com/AmirMSafari).
