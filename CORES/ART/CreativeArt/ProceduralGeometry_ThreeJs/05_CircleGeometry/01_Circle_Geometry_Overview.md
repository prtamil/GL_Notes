# Overview Code 
```js
	constructor( radius = 1, segments = 32, thetaStart = 0, thetaLength = Math.PI * 2 ) {

		super();

		this.type = 'CircleGeometry';

		this.parameters = {
			radius: radius,
			segments: segments,
			thetaStart: thetaStart,
			thetaLength: thetaLength
		};

		segments = Math.max( 3, segments );

		// buffers

		const indices = [];
		const vertices = [];
		const normals = [];
		const uvs = [];

		// helper variables

		const vertex = new Vector3();
		const uv = new Vector2();

		// center point

		vertices.push( 0, 0, 0 );
		normals.push( 0, 0, 1 );
		uvs.push( 0.5, 0.5 );

		for ( let s = 0, i = 3; s <= segments; s ++, i += 3 ) {

			const segment = thetaStart + s / segments * thetaLength;

			// vertex

			vertex.x = radius * Math.cos( segment );
			vertex.y = radius * Math.sin( segment );

			vertices.push( vertex.x, vertex.y, vertex.z );

			// normal

			normals.push( 0, 0, 1 );

			// uvs

			uv.x = ( vertices[ i ] / radius + 1 ) / 2;
			uv.y = ( vertices[ i + 1 ] / radius + 1 ) / 2;

			uvs.push( uv.x, uv.y );

		}

		// indices

		for ( let i = 1; i <= segments; i ++ ) {

			indices.push( i, i + 1, 0 );

		}

		// build geometry

		this.setIndex( indices );
		this.setAttribute( 'position', new Float32BufferAttribute( vertices, 3 ) );
		this.setAttribute( 'normal', new Float32BufferAttribute( normals, 3 ) );
		this.setAttribute( 'uv', new Float32BufferAttribute( uvs, 2 ) );

	}
```


# Re Written Code 
```js
constructor(radius = 1, segments = 32, thetaStart = 0, thetaLength = Math.PI * 2) {

    super();
    this.type = "CircleGeometry";

    // Ensure minimum segments
    segments = Math.max(3, segments);

    const vertices = [];
    const uvs = [];
    const normals = [];
    const indices = [];

    //---------------------------------------------------------------------------
    // MAIN FLOW
    //---------------------------------------------------------------------------

    const centerIndex = addCenterVertex();
    addCircleVertices();
    addCircleNormals();
    addCircleUVs();
    addTriangleFanIndices(centerIndex);

    // Assign geometry data
    this.setIndex(indices);
    this.setAttribute("position", new Float32BufferAttribute(vertices, 3));
    this.setAttribute("normal", new Float32BufferAttribute(normals, 3));
    this.setAttribute("uv", new Float32BufferAttribute(uvs, 2));

    //---------------------------------------------------------------------------
    // FUNCTIONS (vertices, uvs, normals, indices)
    //---------------------------------------------------------------------------

    function addCenterVertex() {
        const centerX = 0;
        const centerY = 0;
        const centerZ = 0;

        vertices.push(centerX, centerY, centerZ);

        const normalX = 0, normalY = 0, normalZ = 1;
        normals.push(normalX, normalY, normalZ);

        const centerU = 0.5, centerV = 0.5;
        uvs.push(centerU, centerV);

        return 0; // center is always index 0
    }

    // Step 1 — Perimeter vertices (parametric sampling)
    function addCircleVertices() {

        for (let segmentIndex = 0; segmentIndex <= segments; segmentIndex++) {

            const t = getPercentageAlongCircle(segmentIndex, segments);
            const angle = interpolateAngle(thetaStart, thetaStart + thetaLength, t);

            const position = convertAngleToXY(angle, radius);

            vertices.push(position.x, position.y, position.z);
        }
    }

    function getPercentageAlongCircle(current, total) {
        return current / total;
    }

    function interpolateAngle(startAngle, arcLength, percentage) {
        return startAngle + arcLength * percentage;
    }

    function convertAngleToXY(angle, radius) {
        const x = radius * Math.cos(angle);
        const y = radius * Math.sin(angle);
        const z = 0;
        return { x, y, z };
    }

    // Step 2 — Normals (same for all circle vertices)
    function addCircleNormals() {
        for (let i = 0; i <= segments; i++) {
            normals.push(0, 0, 1);
        }
    }

    // Step 3 — UV generation
    function addCircleUVs() {

        for (let vertexIndex = 1; vertexIndex <= segments + 1; vertexIndex++) {

            const x = vertices[vertexIndex * 3 + 0];
            const y = vertices[vertexIndex * 3 + 1];

            const uv = convertXYtoUV(x, y, radius);

            uvs.push(uv.u, uv.v);
        }
    }

    function convertXYtoUV(x, y, radius) {
        const u = scaleZeroToOne(shiftZeroToTwo(normalizeMinusOnePlusOne(x)));
        const v = scaleZeroToOne(shiftZeroToTwo(normalizeMinusOnePlusOne(y)));
        return { u, v };

        function normalizeMinusOnePlusOne(value) { return value / radius; }
        function shiftZeroToTwo(value) { return value + 1; }
        function scaleZeroToOne(value) { return value / 2; }
    }

    // Step 4 — Indices (triangle fan)
    function addTriangleFanIndices(centerVertexIndex) {

        for (let edge = 1; edge <= segments; edge++) {

            const a = edge;           // current edge vertex
            const b = edge + 1;       // next edge vertex
            const c = centerVertexIndex; // center

            indices.push(a, b, c);
        }
    }
}

```