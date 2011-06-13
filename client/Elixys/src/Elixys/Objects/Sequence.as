package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class Sequence extends JSONObject
	{
		// Constructor
		public function Sequence(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type() != null) && (Type() != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Data wrappers
		public function Type():String
		{
			return super.flash_proxy::getProperty("type");
		}
		public function Metadata():SequenceMetadata
		{
			// Parse the metadata
			if (m_pMetadata == null)
			{
				m_pMetadata = new SequenceMetadata(null, super.flash_proxy::getProperty("metadata"));
			}
			return m_pMetadata;
		}
		public function Components():Array
		{
			// Parse the buttons
			if (m_pComponents == null)
			{
				m_pComponents = new Array();
				var pComponents:Array = super.flash_proxy::getProperty("components");
				for each (var pComponentObject:Object in pComponents)
				{
					// Ignore the cassettes if specified
					var pComponent:SequenceComponent = new SequenceComponent(null, pComponentObject);
					if ((pComponent.ComponentType == ComponentCassette.TYPE) && m_bHideCassettes)
					{
						continue;
					}
					
					// Add the component
					m_pComponents.push(pComponent);
				}
			}
			return m_pComponents;
		}

		// Hides the cassettes in the Components array
		public function HideCassettes(bHide:Boolean):void
		{
			m_bHideCassettes = bHide;
		}

		// Type
		static public var TYPE:String = "sequence";
		
		// State components
		private var m_pMetadata:SequenceMetadata;
		private var m_pComponents:Array;
		private var m_bHideCassettes:Boolean = false;
	}
}
