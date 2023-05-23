
        #version 410

        #ifdef GL_ES
            precision highp float;
        #endif
        
        // Define PI
        #define PI 3.14

        /* Outputs from the vertex shader */
        varying vec2 tex_coord0;

        // Fetch some dynamic values from Kivy openGL
        uniform float time;
        uniform vec2 resolution;
        uniform vec2 pan;
        uniform float zoom;
        uniform int iterations;

        // Complex Number math by julesb
        // https://github.com/julesb/glsl-util
        // Additions by Johan Karlsson (DonKarlssonSan)

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
        
        vec2 cx_mul(vec2 a, vec2 b) {
            return vec2(a.x*b.x-a.y*b.y, a.x*b.y+a.y*b.x);
        }
        
        vec2 cx_mul(vec2 a, vec2 b, vec2 c) {
            return vec2(cx_mul(cx_mul(a,b), c));
        }

        vec2 cx_mul(vec2 a, vec2 b, vec2 c, vec2 d) {
            return vec2(cx_mul(cx_mul(cx_mul(a,b), c), d));
        }

        vec2 cx_mul(vec2 a, vec2 b, vec2 c, vec2 d, vec2 e) {
            return vec2(cx_mul(cx_mul(cx_mul(cx_mul(a,b), c), d), e));
        }

        ////////////////////////////////////////////////////////////
        // end Complex Number math by julesb
        ////////////////////////////////////////////////////////////

        // DonKarlssonSan's additions to complex number math

        #define cx_abs(a) length(a)
        
        vec2 cx_sub(vec2 a, vec2 b){
            return vec2(a.x - b.x, a.y - b.y);
        }
        
        vec2 cx_sub(vec2 a, vec2 b, vec2 c){
            return cx_sub(vec2(a.x - b.x, a.y - b.y), c);
        }
        
        vec2 cx_sub(vec2 a, vec2 b, vec2 c, vec2 d){
            return cx_sub(vec2(a.x - b.x, a.y - b.y), c, d);
        }
        
        vec2 cx_sub(vec2 a, vec2 b, vec2 c, vec2 d, vec2 e){
            return cx_sub(vec2(a.x - b.x, a.y - b.y), c, d, e);
        }
        
        vec2 cx_add(vec2 a, vec2 b){
            return vec2(a.x + b.x, a.y + b.y);
        }
        
        vec2 cx_add(vec2 a, vec2 b, vec2 c){
            return cx_sub(vec2(a.x + b.x, a.y + b.y), c);
        }
        
        vec2 cx_add(vec2 a, vec2 b, vec2 c, vec2 d){
            return cx_sub(vec2(a.x + b.x, a.y + b.y), c, d);
        }
        
        vec2 cx_add(vec2 a, vec2 b, vec2 c, vec2 d, vec2 e){
            return cx_sub(vec2(a.x + b.x, a.y + b.y), c, d, e);
        }
            
        // Complex power
        // Let z = r(cos θ + i sin θ)
        // Then z^n = r^n (cos nθ + i sin nθ)
        vec2 cx_pow(vec2 a, vec2 n) {
            float angle = atan(a.y, a.x);
            float r = length(a);
            float real = pow(r, n.x) * cos(n.x * angle);
            float im = pow(r, n.x) * sin(n.x * angle);
            return vec2(real, im);
        }


        //// MY CODE ////
        // The function to visualize
        vec2 f(vec2 z) {
            return cx_add(cx_pow(z, vec2(8, 0)), cx_mul(vec2(15, 0), cx_pow(z, vec2(4, 0))), vec2(-16, 0)); // z^4 - 1
        }

        // The derivative of the function to visualize
        vec2 fPrime(vec2 z) {
            return cx_add(cx_mul(vec2(8, 0), cx_pow(z, vec2(7, 0))), cx_mul(vec2(60, 0), cx_pow(z, vec2(3, 0)))); // 4z^3
        }

        vec2 newtons(vec2 z) {
            return cx_sub(z, cx_div(f(z), fPrime(z))); // z - f(z)/f'(z)
        }
        
        vec2 iterate(vec2 z0, int n) {
            for(int i = 0; i < n; i++) {
                z0 = newtons(z0);
            }
            return z0;
        }

        vec2[] roots = vec2[](vec2(-1.00000000000000, 0), vec2(1.00000000000000, 0), vec2(0, 1.00000000000000), vec2(0, -1.00000000000000), vec2(1.41421356237310, 1.41421356237310), vec2(1.41421356237310, -1.41421356237310), vec2(-1.41421356237310, 1.41421356237310), vec2(-1.41421356237310, -1.41421356237310)); // The roots of the function

        vec3[] colors = vec3[](vec3(1.0, 1.0, 0.2), vec3(1.0, 0.4980392156862745, 0.0), vec3(0.596078431372549, 0.3058823529411765, 0.6392156862745098), vec3(0.30196078431372547, 0.6862745098039216, 0.2901960784313726), vec3(0.21568627450980393, 0.49411764705882355, 0.7215686274509804), vec3(0.8941176470588236, 0.10196078431372549, 0.10980392156862745), vec3(0.6, 0.6, 0.6), vec3(0.9686274509803922, 0.5058823529411764, 0.7490196078431373), vec3(0.6509803921568628, 0.33725490196078434, 0.1568627450980392), vec3(1.0, 1.0, 0.2), vec3(1.0, 0.4980392156862745, 0.0), vec3(0.596078431372549, 0.3058823529411765, 0.6392156862745098), vec3(0.30196078431372547, 0.6862745098039216, 0.2901960784313726), vec3(0.21568627450980393, 0.49411764705882355, 0.7215686274509804), vec3(0.8941176470588236, 0.10196078431372549, 0.10980392156862745)); // The colors of the roots

        // Get the color of a given number using the roots of the equation
        vec3 getRootColor(vec2 z) {
            float shortestDistance = -1;
            int shortestIndex = 0;
            
            // Find which root z is closest to
            for(int i = 0; i < roots.length(); i++) {
                float distance = cx_abs(cx_sub(z, roots[i]));
                if(shortestDistance == -1 || distance < shortestDistance) {
                    shortestDistance = distance;
                    shortestIndex = i;
                }
            }
            
            return colors[shortestIndex];
        }

        // Main glsl function
        void main() {
            vec2 pt = vec2(((gl_FragCoord.x - resolution.x / 2) - pan.x) / zoom, ((gl_FragCoord.y - resolution.y / 2) - pan.y) / zoom);
            
            // TODO: Optimize by checking if it equals a root while iterating to reduce iteration count
            vec2 iterResult = iterate(pt, iterations);
            
            gl_FragColor = vec4(getRootColor(iterResult), 1);
        }
        