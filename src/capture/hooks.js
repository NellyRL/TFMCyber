(function() {
    // This function send the information to the main script
    async function apiCallDetected(apiCall) {
      // Check if the function in the main script is defined
        if (typeof window.pyNotify !== "undefined") {
            // Send the information
            window.pyNotify(apiCall);
            // Stop the execution
            debugger;

        }
    }

    // Define property method allows us to force a change in the API methods
    Object.defineProperty(navigator, "geolocation", {
        // Proxy definition for capture all navigator.geolocation events
        value: new Proxy(navigator.geolocation, {
          // The get method intercepts the API calls
          get(target, prop, receiver) {
            // Intercept calls to navigator.geolocation
            if (typeof target[prop] === "function") {
              return async function(...args) {
                await apiCallDetected(`navigator.geolocation.${prop}`);
                // return the API call for a normal execution
                return Reflect.apply(target[prop], target, args);
              };
            }
            return Reflect.get(target, prop, receiver);
          }
        }),
        // Allows future modifications on navigator.geolocation
        configurable: true  
      });
      
      if (navigator.mediaDevices) {
        navigator.mediaDevices.getUserMedia = new Proxy(navigator.mediaDevices.getUserMedia, {
            apply(target, thisArg, args) {
                apiCallDetected("navigator.mediaDevices.getUserMedia");
                return Reflect.apply(target, thisArg, args);
            }
        });
    }

    if (navigator.clipboard) {
        navigator.clipboard.readText = new Proxy(navigator.clipboard.readText, {
            apply(target, thisArg, args) {
                apiCallDetected("navigator.clipboard.readText");
                return Reflect.apply(target, thisArg, args);
            }
        });

        navigator.clipboard.writeText = new Proxy(navigator.clipboard.writeText, {
            apply(target, thisArg, args) {
                apiCallDetected("navigator.clipboard.writeText");
                return Reflect.apply(target, thisArg, args);
            }
        });
    }

    window.fetch = new Proxy(window.fetch, {
        apply(target, thisArg, args) {
            apiCallDetected(`fetch -> ${args[0]}`);
            return Reflect.apply(target, thisArg, args);
        }
    });

    const originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url) {
        apiCallDetected(`XMLHttpRequest -> ${method} ${url}`);
        return originalOpen.apply(this, arguments);
    };

})();
