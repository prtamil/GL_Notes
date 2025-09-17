## MonoGame Overview
1. SpriteBatch
2. DrawString
3. Lerp, InvLerp, ReMap 
### Important Point vs Vectors
1. almost frameworks use vectors for points its not actual vectors its position vectors. 
2. Based on that you need to think.
### important Math function
1. Lerp
2. InverseLerp
3. Math.Clamp
4. ReMap
5. Min, Max
### Techniques
Focus Object on Mouse 
```c#
Vector2 objPosition = new Vector2(100,100);
Vector2 mousePosition = new Vector2(mouseState.X, mouseState.Y);
Vector2 diff = mousePosition - objPosition;
float angle = Math.Atan2(diff.Y, diff.X);

_spriteBatch.DrawLine(objPosition, 10Length, angle, Color.White);
