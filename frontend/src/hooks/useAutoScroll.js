import { useCallback, useEffect, useRef, useState } from "react";

export default function useAutoScroll(dependencies = []) {
  const containerRef = useRef(null);
  const [isNearBottom, setIsNearBottom] = useState(true);
  const [hasNewMessages, setHasNewMessages] = useState(false);

  const scrollToBottom = useCallback((behavior = "smooth") => {
    const container = containerRef.current;
    if (!container) return;

    container.scrollTo({
      top: container.scrollHeight,
      behavior,
    });

    setHasNewMessages(false);
  }, []);

  const handleScroll = useCallback(() => {
    const container = containerRef.current;
    if (!container) return;

    const distanceFromBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight;

    const nearBottom = distanceFromBottom < 120;
    setIsNearBottom(nearBottom);

    if (nearBottom) {
      setHasNewMessages(false);
    }
  }, []);

  useEffect(() => {
    if (!containerRef.current) return;

    if (isNearBottom) {
      scrollToBottom("smooth");
    } else {
      setHasNewMessages(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isNearBottom, scrollToBottom, ...dependencies]);

  return {
    containerRef,
    handleScroll,
    scrollToBottom,
    hasNewMessages,
    isNearBottom,
  };
}
