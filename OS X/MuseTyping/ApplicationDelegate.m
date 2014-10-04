#import "ApplicationDelegate.h"

@interface ApplicationDelegate ()
@property (nonatomic, strong) NSMutableArray *alphabet;
@property (nonatomic) NSUInteger letter;
@property (nonatomic) BOOL typing;
@property (nonatomic, strong) NSTimer *timer;
@end

@implementation ApplicationDelegate

@synthesize menubarController = _menubarController;

#pragma mark -

void *kContextActivePanel = &kContextActivePanel;

- (void)observeValueForKeyPath:(NSString *)keyPath ofObject:(id)object change:(NSDictionary *)change context:(void *)context
{
    if (context == kContextActivePanel) {
    }
    else {
        [super observeValueForKeyPath:keyPath ofObject:object change:change context:context];
    }
}

#pragma mark - NSApplicationDelegate

- (void)applicationDidFinishLaunching:(NSNotification *)notification
{
    // Install icon into the menu bar
    self.menubarController = [[MenubarController alloc] init];
    self.typing = NO;
    
    self.alphabet = [[NSMutableArray alloc] init];
    for (char a = 'a'; a <= 'z'; a++)
    {
        [self.alphabet addObject:[NSString stringWithFormat:@"%c", a]];
    }
    self.menubarController.statusItemView.action = @selector(togglePanel:);
}

- (NSApplicationTerminateReply)applicationShouldTerminate:(NSApplication *)sender
{
    // Explicitly remove the icon from the menu bar
    self.menubarController = nil;
    return NSTerminateNow;
}

#pragma mark - Actions

- (IBAction)togglePanel:(id)sender
{
    self.menubarController.hasActiveIcon = !self.menubarController.hasActiveIcon;
    self.typing = !self.typing;
    [self.menubarController.statusItem setTitle:nil];
    self.menubarController.statusItemView.image = self.typing ? nil : [NSImage imageNamed:@"Status"];
    self.menubarController.statusItemView.alternateImage = self.typing ? nil : [NSImage imageNamed:@"StatusHighlighted"];
    if (self.typing) {
        self.timer = [NSTimer scheduledTimerWithTimeInterval:1.0
                                                      target:self
                                                    selector:@selector(loopAlphabet)
                                                    userInfo:nil
                                                     repeats:YES];
    }
    else {
        [self.timer invalidate];
        self.timer = nil;
    }
}

- (void)loopAlphabet {
    self.menubarController.statusItemView.alternateImage = [NSImage imageNamed:[NSString stringWithFormat:@"%lu", (unsigned long)self.letter]];
    self.letter = (self.letter + 1) % 26;
    
    
    int pid = [[NSProcessInfo processInfo] processIdentifier];
    NSPipe *pipe = [NSPipe pipe];
    
    NSTask *task = [[NSTask alloc] init];
    task.launchPath = @"/usr/bin/automator";
    task.arguments = @[[NSString stringWithFormat:@"~/.museTyping/%lu.workflow", (unsigned long)self.letter]];
    task.standardOutput = pipe;
    
    [task launch];
}

#pragma mark - PanelControllerDelegate

- (StatusItemView *)statusItemViewForPanelController:(PanelController *)controller
{
    return self.menubarController.statusItemView;
}

@end
