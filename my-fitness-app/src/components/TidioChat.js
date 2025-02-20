// components/TidioChat.js
import { useEffect } from 'react';

const TidioChat = () => {
    useEffect(() => {
        // Tidio integration script
        const script = document.createElement("script");
        script.src = "//code.tidio.co/6w4i2erscvqukmvtpaknboyyp03zlkxe.js"; // Your Tidio code
        script.async = true;
        document.body.appendChild(script);

        return () => {
            // Cleanup the script on unmount
            document.body.removeChild(script);
        };
    }, []);

    return null;
};

export default TidioChat;
