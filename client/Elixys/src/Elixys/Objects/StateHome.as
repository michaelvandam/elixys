package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class StateHome extends State
	{
		// Constructor
		public function StateHome(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((ClientState() != null) && (ClientState().Screen() != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}
				
		// Data wrappers
		public function Buttons():Array
		{
			// Parse the buttons
			if (m_pButtons == null)
			{
				m_pButtons = new Array();
				var pButtons:Array = super.flash_proxy::getProperty("buttons");
				for each (var pButtonObject:Object in pButtons)
				{
					var pButton:Button = new Button(null, pButtonObject);
					m_pButtons.push(pButton);
				}
			}
			return m_pButtons;
		}
		
		// Type
		static public var TYPE:String = "HOME";
		
		// State components
		private var m_pButtons:Array;
	}
}
