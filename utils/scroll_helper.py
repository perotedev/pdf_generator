# -*- coding: utf-8 -*-
"""
Helper para adicionar suporte a scroll com roda do mouse em widgets
"""

def bind_mousewheel(widget, canvas_or_scrollable):
    """
    Vincula eventos de scroll do mouse a um widget.
    
    Args:
        widget: Widget que receberá os eventos de scroll
        canvas_or_scrollable: Canvas ou ScrollableFrame que será scrollado
    """
    def _on_mousewheel(event):
        # Windows/macOS usam event.delta, Linux usa event.num
        if hasattr(event, 'delta'):
            # Windows e macOS
            delta = event.delta
            if delta > 0:
                canvas_or_scrollable.yview_scroll(-1, "units")
            elif delta < 0:
                canvas_or_scrollable.yview_scroll(1, "units")
        elif hasattr(event, 'num'):
            # Linux
            if event.num == 4:  # Scroll up
                canvas_or_scrollable.yview_scroll(-1, "units")
            elif event.num == 5:  # Scroll down
                canvas_or_scrollable.yview_scroll(1, "units")
    
    # Bind para diferentes sistemas operacionais
    widget.bind("<MouseWheel>", _on_mousewheel)  # Windows/macOS
    widget.bind("<Button-4>", _on_mousewheel)    # Linux scroll up
    widget.bind("<Button-5>", _on_mousewheel)    # Linux scroll down
    
    return _on_mousewheel

def bind_mousewheel_to_scrollable_frame(scrollable_frame):
    """
    Vincula eventos de scroll do mouse a um CTkScrollableFrame.
    
    Args:
        scrollable_frame: CTkScrollableFrame que será scrollado
    """
    def _on_mousewheel(event):
        # Windows/macOS usam event.delta, Linux usa event.num
        if hasattr(event, 'delta'):
            # Windows e macOS
            delta = event.delta
            if delta > 0:
                scrollable_frame._parent_canvas.yview_scroll(-1, "units")
            elif delta < 0:
                scrollable_frame._parent_canvas.yview_scroll(1, "units")
        elif hasattr(event, 'num'):
            # Linux
            if event.num == 4:  # Scroll up
                scrollable_frame._parent_canvas.yview_scroll(-1, "units")
            elif event.num == 5:  # Scroll down
                scrollable_frame._parent_canvas.yview_scroll(1, "units")
    
    # Bind para diferentes sistemas operacionais
    scrollable_frame.bind("<MouseWheel>", _on_mousewheel)  # Windows/macOS
    scrollable_frame.bind("<Button-4>", _on_mousewheel)    # Linux scroll up
    scrollable_frame.bind("<Button-5>", _on_mousewheel)    # Linux scroll down
    
    # Também vincula aos filhos do frame
    for child in scrollable_frame.winfo_children():
        child.bind("<MouseWheel>", _on_mousewheel)
        child.bind("<Button-4>", _on_mousewheel)
        child.bind("<Button-5>", _on_mousewheel)
    
    return _on_mousewheel
