## Hi there 👋



from collections import deque
def bfs(t,s):
    v,q=[],deque([s])
    while q:
        n=q.popleft()
        if n not in v:v.append(n);q+=t[n]
    return v

t={};n=int(input("Nodes: "))
for _ in range(n):
    x=input("Node: ");c=input(f"Children of {x}: ").replace(" ","")
    t[x]=c.split(",") if c else []
s=input("Start: ")
print("BFS Traversal:"," → ".join(bfs(t,s)))



from collections import defaultdict
def dfs(g,s,v=set()):
    v.add(s);print(s,end=" → " if len(v)<len(g) else "")
    for n in g[s]:
        if n not in v:dfs(g,n,v)

g=defaultdict(list)
for _ in range(int(input("Nodes: "))):
    x=input("Node: ");c=input(f"Children of {x}: ").replace(" ","")
    g[x]=c.split(",") if c else []
s=input("Start: ")
print("DFS Traversal: ",end="");dfs(g,s)




<!--
**namaninnovates/namaninnovates** is a ✨ _special_ ✨ repository because its `README.md` (this file) appears on your GitHub profile.

Here are some ideas to get you started:

- 🔭 I’m currently working on ...
- 🌱 I’m currently learning ...
- 👯 I’m looking to collaborate on ...
- 🤔 I’m looking for help with ...
- 💬 Ask me about ...
- 📫 How to reach me: ...
- 😄 Pronouns: ...
- ⚡ Fun fact: ...
-->
