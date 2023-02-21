#version 330

#define PI 3.14

#ifdef GL_ES
precision highp float;
#endif

uniform float time;
uniform vec2  resolution;
uniform float zoom;
uniform vec2 mouse;

// Complex Number math by julesb
// https://github.com/julesb/glsl-util
// Additions by Johan Karlsson (DonKarlssonSan)

#define cx_mul(a, b) vec2(a.x*b.x-a.y*b.y, a.x*b.y+a.y*b.x)
#define cx_div(a, b) vec2(((a.x*b.x+a.y*b.y)/(b.x*b.x+b.y*b.y)),((a.y*b.x-a.x*b.y)/(b.x*b.x+b.y*b.y)))
#define cx_modulus(a) length(a)
#define cx_conj(a) vec2(a.x, -a.y)
#define cx_arg(a) atan(a.y, a.x)
#define cx_sin(a) vec2(sin(a.x) * cosh(a.y), cos(a.x) * sinh(a.y))
#define cx_cos(a) vec2(cos(a.x) * cosh(a.y), -sin(a.x) * sinh(a.y))

vec2 cx_sqrt(vec2 a) {
    float r = length(a);
    float rpart = sqrt(0.5*(r+a.x));
    float ipart = sqrt(0.5*(r-a.x));
    if (a.y < 0.0) ipart = -ipart;
    return vec2(rpart,ipart);
}

vec2 cx_tan(vec2 a) {return cx_div(cx_sin(a), cx_cos(a)); }

vec2 cx_log(vec2 a) {
    float rpart = sqrt((a.x*a.x)+(a.y*a.y));
    float ipart = atan(a.y,a.x);
    if (ipart > PI) ipart=ipart-(2.0*PI);
    return vec2(log(rpart),ipart);
}

vec2 cx_mobius(vec2 a) {
    vec2 c1 = a - vec2(1.0,0.0);
    vec2 c2 = a + vec2(1.0,0.0);
    return cx_div(c1, c2);
}

vec2 cx_z_plus_one_over_z(vec2 a) {
    return a + cx_div(vec2(1.0,0.0), a);
}

vec2 cx_z_squared_plus_c(vec2 z, vec2 c) {
    return cx_mul(z, z) + c;
}

vec2 cx_sin_of_one_over_z(vec2 z) {
    return cx_sin(cx_div(vec2(1.0,0.0), z));
}

////////////////////////////////////////////////////////////
// end Complex Number math by julesb
////////////////////////////////////////////////////////////

// DonKarlssonSan's additions to complex number math

#define cx_sub(a, b) vec2(a.x - b.x, a.y - b.y)
#define cx_add(a, b) vec2(a.x + b.x, a.y + b.y)
#define cx_abs(a) length(a)
vec2 cx_to_polar(vec2 a) {
    float phi = atan(a.y / a.x);
    float r = length(a);
    return vec2(r, phi); 
}
    
// Complex power
// Let z = r(cos θ + i sin θ)
// Then z^n = r^n (cos nθ + i sin nθ)
vec2 cx_pow(vec2 a, float n) {
    float angle = atan(a.y, a.x);
    float r = length(a);
    float real = pow(r, n) * cos(n*angle);
    float im = pow(r, n) * sin(n*angle);
    return vec2(real, im);
}


//// MY CODE ////
vec2 f(vec2 z, vec2 c) {
	return cx_add(cx_pow(z, 2), c);
}


int iterate(vec2 c, int n) {
	vec2 z = vec2(0, 0);
	
    for(int i = 0; i < n; i++) {
		z = f(z, c);
		
		if (cx_abs(z) > 2) {
			return i;
		}
	}
    return n;
}

float remap(float min1, float max1, float min2, float max2, float val){
	return min1 + (val - min1) * (max2 - min2) / (max1 - min1);
}


// Main glsl function
void main() {
	vec2 offset = vec2(resolution.x / 2, resolution.y / 2);
    vec2 pt = vec2(gl_FragCoord.x - offset.x, gl_FragCoord.y - offset.y);
	vec2 remapped = vec2(remap(0, resolution.x, -1.5, 1.5, pt.x), remap(0, resolution.y, -1.5, 1.5, pt.y));
   
    int iterations = int(min(1, time / 5.0) * 100.0);
    int iterResult = iterate(remapped, 100);
    float val = iterResult / 100;
    
    gl_FragColor = vec4(val, val, val, 1);
}

