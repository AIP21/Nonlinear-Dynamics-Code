#version 330

#extension GL_OES_standard_derivatives : enable

#ifdef GL_ES
precision highp float;
#endif

uniform float time;
uniform vec2  resolution;
uniform float zoom;

#define PI 3.14

mat2 rotate3d(float angle)
{
    return mat2(cos(angle), -sin(angle), sin(angle), cos(angle));
}

float f=0.005+sin(time);
void main()
{
    vec2 p = (gl_FragCoord.xy * 2.0 - resolution) / min(resolution.x, resolution.y);
    p = rotate3d((time * min(2.0*time,time*20.0)) * PI) * p;
    float t;
    
       // t = f / abs(0.8 - length(p));
	
	t = 0.045 / abs(0.8 - length(p));
	t += 0.035 / abs(1.0 - length(p-vec2(0.05,0.0)));
     
    gl_FragColor = vec4(vec3(t)  * vec3(0.25*(tan(time)+5.0), p.y*1.0, 1.0), 9.0);
}