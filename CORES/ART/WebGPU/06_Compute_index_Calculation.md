All three IDs (`local_invocation_id`, `workgroup_id`, `global_invocation_id`) are tied together by **workgroup_size** and **num_workgroups**.

---

## 1. Known quantities

- `workgroup_size = (Wx, Wy, Wz)` → how many threads per workgroup.
- `num_workgroups = (Nx, Ny, Nz)` → how many workgroups in the grid.
    

From these:

- **Total grid size** = `(Wx * Nx, Wy * Ny, Wz * Nz)` = `(Gx, Gy, Gz)`.
    

---

## 2. Core equations

### (a) From workgroup_id + local_invocation_id → global_invocation_id

global_id=workgroup_id×workgroup_size+local_idglobal\_id = workgroup\_id \times workgroup\_size + local\_idglobal_id=workgroup_id×workgroup_size+local_id

or per axis:
```ini
global_id.x = workgroup_id.x * Wx + local_id.x
global_id.y = workgroup_id.y * Wy + local_id.y
global_id.z = workgroup_id.z * Wz + local_id.z

```
---

### (b) From global_invocation_id → workgroup_id

workgroup_id=global_id÷workgroup_sizeworkgroup\_id = global\_id \div workgroup\_sizeworkgroup_id=global_id÷workgroup_size

(integer division, per axis)

```ini
workgroup_id.x = global_id.x / Wx
workgroup_id.y = global_id.y / Wy
workgroup_id.z = global_id.z / Wz

```

---

### (c) From global_invocation_id → local_invocation_id

local_id=global_idmod  workgroup_sizelocal\_id = global\_id \mod workgroup\_sizelocal_id=global_idmodworkgroup_size

(remainder per axis)

```ini
local_id.x = global_id.x % Wx
local_id.y = global_id.y % Wy
local_id.z = global_id.z % Wz

```


---

### (d) From local_invocation_id + global_invocation_id → workgroup_id

Just rearrange (a):

```ini
workgroup_id.x = (global_id.x - local_id.x) / Wx
workgroup_id.y = (global_id.y - local_id.y) / Wy
workgroup_id.z = (global_id.z - local_id.z) / Wz

```


---

## 3. Flattened (1D index form)

Sometimes you want a single index into a buffer instead of `(x,y,z)` coords.

- **Global index:**
    
```ini
index = global_id.x + global_id.y * Gx + global_id.z * Gx * Gy

```


- **Local index (inside workgroup):**
    
```ini
local_index = local_id.x + local_id.y * Wx + local_id.z * Wx * Wy

```


- **Workgroup linear index:**
```ini
wg_index = workgroup_id.x + workgroup_id.y * Nx + workgroup_id.z * Nx * Ny

```

---

## ✅ Summary (cheat sheet)

```ini
global_id   = workgroup_id * workgroup_size + local_id
workgroup_id = global_id / workgroup_size   (integer division)
local_id     = global_id % workgroup_size   (modulo)

```